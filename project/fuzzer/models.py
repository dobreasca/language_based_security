from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Payload:
    """A generated test input plus its grammar expectation."""

    value: str
    mode: str
    expected_valid: bool
    strategy: str
    description: str = ""
    metadata: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["metadata"] = self.metadata or {}
        return data


@dataclass
class FuzzResult:
    index: int
    payload: Payload
    method: str
    url: str
    request_body: str
    status_code: Optional[int]
    elapsed_ms: Optional[float]
    outcome: str
    detail: str
    response_excerpt: str = ""
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "mode": self.payload.mode,
            "strategy": self.payload.strategy,
            "description": self.payload.description,
            "expected_valid": self.payload.expected_valid,
            "payload": self.payload.value,
            "method": self.method,
            "url": self.url,
            "request_body": self.request_body,
            "status_code": self.status_code,
            "elapsed_ms": self.elapsed_ms,
            "outcome": self.outcome,
            "detail": self.detail,
            "response_excerpt": self.response_excerpt,
            "error": self.error,
        }