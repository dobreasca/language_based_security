from __future__ import annotations

import json
import time
from typing import Dict, Iterable, List
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from .classifier import classify_response
from .models import FuzzResult, Payload


def parse_headers(
    header_values: List[str] | None,
    bearer_token: str | None,
) -> Dict[str, str]:
    headers: Dict[str, str] = {}

    for raw in header_values or []:
        if ":" not in raw:
            raise ValueError(f"Header must use 'Name: value' format: {raw}")

        name, value = raw.split(":", 1)
        headers[name.strip()] = value.strip()

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    return headers


def parse_extra_fields(values: list[str]) -> dict[str, str]:
    """
    Converts CLI values like:

        --extra-field action=0
        --extra-field submitNewsletter=Subscribe

    into:

        {
            "action": "0",
            "submitNewsletter": "Subscribe"
        }
    """

    result: dict[str, str] = {}

    for item in values:
        if "=" not in item:
            raise ValueError(f"Invalid extra field format: {item}")

        key, value = item.split("=", 1)

        result[key] = value

    return result


def with_query_payload(url: str, payload: str) -> str:
    parts = urlsplit(url)

    existing = parse_qsl(parts.query, keep_blank_values=True)
    extra = parse_qsl(payload, keep_blank_values=True)

    if not extra:
        extra = [("fuzz", payload)]

    query = urlencode(existing + extra, doseq=True)

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            query,
            parts.fragment,
        )
    )


def build_request(
    payload: Payload,
    target: str,
    method: str,
    body_format: str,
    field: str,
    target_type: str,
    upload_field: str,
    extra_fields: dict[str, str],
) -> tuple[str, dict, str]:
    method = method.upper()

    kwargs: dict = {}

    # ============================================================
    # QUERY PARAMETER FUZZING
    # ============================================================

    if payload.mode == "params" and (
        method == "GET" or body_format == "query"
    ):
        return (
            with_query_payload(target, payload.value),
            kwargs,
            "<query string>",
        )

    # ============================================================
    # FILE UPLOAD FUZZING
    # ============================================================

    if payload.mode == "upload":
        meta = payload.metadata or {}

        filename = meta.get("filename", payload.value)
        mime_type = meta.get("mime_type", "application/octet-stream")

        content = bytes.fromhex(meta.get("content", "78"))

        kwargs["files"] = {
            upload_field: (
                filename,
                content,
                mime_type,
            )
        }

        request_body = (
            f"multipart file {upload_field}={filename}; "
            f"mime={mime_type}; "
            f"bytes={len(content)}"
        )

        return target, kwargs, request_body

    # ============================================================
    # JSON BODY
    # ============================================================

    if body_format == "json":

        # Start with static fields
        body = extra_fields.copy()

        # Strapi requires wrapping inside "data"
        if target_type == "strapi":
            body = {
                "data": {
                    **body,
                    field: payload.value,
                }
            }

        else:
            body[field] = payload.value

        kwargs["json"] = body

        return (
            target,
            kwargs,
            json.dumps(body, ensure_ascii=False),
        )

    # ============================================================
    # FORM BODY
    # ============================================================

    if body_format == "form":

        # Start with static fields
        body = extra_fields.copy()

        # Add fuzzed field
        body[field] = payload.value

        kwargs["data"] = body

        return (
            target,
            kwargs,
            urlencode(body),
        )

    # ============================================================
    # RAW BODY
    # ============================================================

    if body_format == "raw":
        kwargs["data"] = payload.value

        return (
            target,
            kwargs,
            payload.value,
        )

    # ============================================================
    # QUERY BODY
    # ============================================================

    if body_format == "query":
        return (
            with_query_payload(
                target,
                f"{field}={payload.value}",
            ),
            kwargs,
            "<query string>",
        )

    raise ValueError(f"Unsupported body format: {body_format}")


def send_payloads(
    payloads: Iterable[Payload],
    target: str,
    method: str,
    body_format: str,
    field: str,
    target_type: str,
    upload_field: str,
    headers: Dict[str, str],
    timeout: float,
    verify_tls: bool,
    extra_fields: dict[str, str],
) -> List[FuzzResult]:

    session = requests.Session()

    session.headers.update(headers)

    results: List[FuzzResult] = []

    for index, payload in enumerate(payloads, start=1):

        url, request_kwargs, request_body = build_request(
            payload=payload,
            target=target,
            method=method,
            body_format=body_format,
            field=field,
            target_type=target_type,
            upload_field=upload_field,
            extra_fields=extra_fields,
        )

        status_code = None
        elapsed_ms = None
        excerpt = ""
        error = ""

        started = time.perf_counter()

        try:
            response = session.request(
                method=method.upper(),
                url=url,
                timeout=timeout,
                verify=verify_tls,
                **request_kwargs,
            )

            elapsed_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )

            status_code = response.status_code

            excerpt = response.text[:5000].replace("\n", " ").replace("\r", " ")

        except requests.RequestException as exc:

            elapsed_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )

            error = str(exc)

        outcome, detail = classify_response(
            expected_valid=payload.expected_valid,
            status_code=status_code,
            response_text=excerpt,
            error=error,
        )

        results.append(
            FuzzResult(
                index=index,
                payload=payload,
                method=method.upper(),
                url=url,
                request_body=request_body,
                status_code=status_code,
                elapsed_ms=elapsed_ms,
                outcome=outcome,
                detail=detail,
                response_excerpt=excerpt,
                error=error,
            )
        )

    return results