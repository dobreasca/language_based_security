from __future__ import annotations

from typing import Optional


SUCCESS_CODES = {200, 201, 202, 204, 301, 302, 303, 307, 308}

REJECTION_CODES = {
    400,
    401,
    403,
    404,
    405,
    409,
    413,
    415,
    422,
    429,
}


def classify_response(
    expected_valid: bool,
    status_code: Optional[int],
    error: str = "",
) -> tuple[str, str]:
    if error:
        return "request_error", error

    if status_code is None:
        return "request_error", "No HTTP status code was returned"

    if 500 <= status_code <= 599:
        return "server_error", "Server returned 5xx; possible crash or unhandled edge case"

    accepted = status_code in SUCCESS_CODES or 200 <= status_code <= 299
    rejected = status_code in REJECTION_CODES or 400 <= status_code <= 499

    if expected_valid and accepted:
        return "valid_accepted", "Expected-valid input was accepted"

    if expected_valid and rejected:
        return "valid_rejected", "Expected-valid input was rejected"

    if not expected_valid and accepted:
        return (
            "invalid_accepted",
            "Expected-invalid input was accepted; potential validation inconsistency",
        )

    if not expected_valid and rejected:
        return "invalid_rejected", "Expected-invalid input was rejected"

    return "unclear", "Could not confidently classify response"