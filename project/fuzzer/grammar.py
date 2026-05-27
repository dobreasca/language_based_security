from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Pattern


@dataclass(frozen=True)
class GrammarRule:
    name: str
    regex: str
    description: str

    def compile(self) -> Pattern[str]:
        return re.compile(self.regex)


EMAIL_GRAMMAR = GrammarRule(
    name="email",
    regex=(
        r"^[A-Za-z0-9_%+-]+"
        r"(?:\.[A-Za-z0-9_%+-]+)*"
        r"@"
        r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
        r"[A-Za-z]{2,}$"
    ),
    description="Email grammar that disallows leading/trailing/consecutive dots and malformed domains",
)


HTTP_PARAM_GRAMMAR = GrammarRule(
    name="http_parameter",
    regex=r"^[A-Za-z_][A-Za-z0-9_]*=[A-Za-z0-9._~%+\-:@,]*$",
    description="Simplified HTTP query parameter grammar: key=value",
)


POSITIVE_INTEGER_PARAM_GRAMMAR = GrammarRule(
    name="positive_integer_parameter",
    regex=r"^[A-Za-z_][A-Za-z0-9_]*=[1-9][0-9]*$",
    description="HTTP parameter whose value should be a positive integer",
)


SAFE_FILENAME_GRAMMAR = GrammarRule(
    name="safe_filename",
    regex=r"^[A-Za-z0-9._-]+\.(txt|png|jpg|jpeg|webp|pdf)$",
    description="Safe upload filename grammar with restricted extensions",
)


URL_GRAMMAR = GrammarRule(
    name="url",
    regex=r"^https?://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]*)?$",
    description="Simplified HTTP/HTTPS URL grammar",
)


GRAMMARS = {
    "email": EMAIL_GRAMMAR,
    "params": HTTP_PARAM_GRAMMAR,
    "upload": SAFE_FILENAME_GRAMMAR,
    "url": URL_GRAMMAR,
}


def get_grammar(mode: str) -> GrammarRule:
    if mode not in GRAMMARS:
        raise ValueError(f"No grammar defined for mode: {mode}")

    return GRAMMARS[mode]


def is_valid_for_mode(mode: str, value: str) -> bool:
    grammar = get_grammar(mode)
    return grammar.compile().fullmatch(value) is not None

def is_valid_upload_payload(filename: str, mime_type: str, content: bytes) -> bool:
    if not is_valid_for_mode("upload", filename):
        return False

    lowered = filename.lower()

    if lowered.endswith(".png"):
        return mime_type == "image/png" and content.startswith(b"\x89PNG")

    if lowered.endswith(".jpg") or lowered.endswith(".jpeg"):
        return mime_type == "image/jpeg" and content.startswith(b"\xff\xd8")

    if lowered.endswith(".webp"):
        return mime_type == "image/webp" and content.startswith(b"RIFF")

    if lowered.endswith(".pdf"):
        return mime_type == "application/pdf" and content.startswith(b"%PDF")

    if lowered.endswith(".txt"):
        return mime_type == "text/plain" and len(content) > 0

    return False