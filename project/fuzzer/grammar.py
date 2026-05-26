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
    regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
    description="Simplified web email grammar: local-part@domain.tld",
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


SLUG_GRAMMAR = GrammarRule(
    name="slug",
    regex=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    description="URL-safe slug grammar",
)


URL_GRAMMAR = GrammarRule(
    name="url",
    regex=r"^https?://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]*)?$",
    description="Simplified HTTP/HTTPS URL grammar",
)


TEXT_GRAMMAR = GrammarRule(
    name="text",
    regex=r"^[^\x00\r\n]{1,255}$",
    description="Simple single-line text grammar without null bytes or newlines",
)


GRAMMARS = {
    "email": EMAIL_GRAMMAR,
    "params": HTTP_PARAM_GRAMMAR,
    "upload": SAFE_FILENAME_GRAMMAR,
    "slug": SLUG_GRAMMAR,
    "url": URL_GRAMMAR,
    "text": TEXT_GRAMMAR,
}


def get_grammar(mode: str) -> GrammarRule:
    if mode not in GRAMMARS:
        raise ValueError(f"No grammar defined for mode: {mode}")

    return GRAMMARS[mode]


def is_valid_for_mode(mode: str, value: str) -> bool:
    grammar = get_grammar(mode)
    return grammar.compile().fullmatch(value) is not None