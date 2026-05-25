from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, List

from .models import FuzzResult


def summarize(results: Iterable[FuzzResult]) -> dict:
    rows = list(results)

    by_outcome = Counter(r.outcome for r in rows)
    by_status = Counter(str(r.status_code) for r in rows)

    interesting = []

    for result in rows:
        if result.outcome in {
            "invalid_accepted",
            "valid_rejected",
            "server_error",
            "request_error",
        }:
            interesting.append(result)

    return {
        "total": len(rows),
        "outcomes": dict(by_outcome),
        "status_codes": dict(by_status),
        "interesting_count": len(interesting),
        "interesting_examples": [r.to_dict() for r in interesting[:10]],
    }


def write_csv(results: List[FuzzResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = [r.to_dict() for r in results]

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json_summary(results: List[FuzzResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize(results)

    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def print_summary(results: List[FuzzResult]) -> None:
    summary = summarize(results)

    print("\n=== Fuzzing summary ===")
    print(f"Total tests: {summary['total']}")

    print("Outcomes:")
    for name, count in sorted(summary["outcomes"].items()):
        print(f"  - {name}: {count}")

    print("Status codes:")
    for code, count in sorted(summary["status_codes"].items()):
        print(f"  - {code}: {count}")

    print(f"Interesting findings: {summary['interesting_count']}")

    if summary["interesting_examples"]:
        print("\nFirst interesting examples:")

        for item in summary["interesting_examples"][:5]:
            print(
                f"  #{item['index']} {item['outcome']} "
                f"status={item['status_code']} "
                f"payload={item['payload']!r} "
                f"detail={item['detail']}"
            )