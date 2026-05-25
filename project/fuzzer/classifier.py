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


DEFAULT_REJECTION_PATTERNS = [
    "invalid",
    "not valid",
    "please enter",
    "please provide",
    "required",
    "is required",
    "error",
    "failed",
    "failure",
    "not allowed",
    "forbidden",
    "denied",
    "alert-danger",
    "has-error",
    "form-error",
]


DEFAULT_SUCCESS_PATTERNS = [
    "success",
    "successful",
    "successfully",
    "thank you",
    "subscribed",
    "created",
    "saved",
    "updated",
    "alert-success",
]


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()

    for pattern in patterns:
        if pattern.lower() in lowered:
            return True

    return False


def classify_response(
    expected_valid: bool,
    status_code: Optional[int],
    response_text: str = "",
    error: str = "",
    rejection_patterns: list[str] | None = None,
    success_patterns: list[str] | None = None,
) -> tuple[str, str]:
    if error:
        return "request_error", error

    if status_code is None:
        return "request_error", "No HTTP status code was returned"

    if 500 <= status_code <= 599:
        return "server_error", "Server returned 5xx; possible crash or unhandled edge case"

    rejection_patterns = rejection_patterns or DEFAULT_REJECTION_PATTERNS
    success_patterns = success_patterns or DEFAULT_SUCCESS_PATTERNS

    body_says_rejected = contains_any(response_text, rejection_patterns)
    body_says_success = contains_any(response_text, success_patterns)

    if body_says_rejected and not body_says_success:
        accepted = False
        rejected = True
        signal = "response body contained rejection indicator"
    elif body_says_success and not body_says_rejected:
        accepted = True
        rejected = False
        signal = "response body contained success indicator"
    else:
        accepted = status_code in SUCCESS_CODES or 200 <= status_code <= 299
        rejected = status_code in REJECTION_CODES or 400 <= status_code <= 499
        signal = "classified using HTTP status code"

    if expected_valid and accepted:
        return "valid_accepted", f"Expected-valid input was accepted; {signal}"

    if expected_valid and rejected:
        return "valid_rejected", f"Expected-valid input was rejected; {signal}"

    if not expected_valid and accepted:
        return (
            "invalid_accepted",
            f"Expected-invalid input was accepted; {signal}",
        )

    if not expected_valid and rejected:
        return "invalid_rejected", f"Expected-invalid input was rejected; {signal}"

    return "unclear", "Could not confidently classify response"