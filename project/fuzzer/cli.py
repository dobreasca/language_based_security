from __future__ import annotations

import argparse


def setup_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Grammar-based fuzzer for exposing client-server validation inconsistencies"
    )

    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Target URL to fuzz, e.g. http://localhost:1337/api/contact-submissions",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["email", "upload", "params"],
        required=True,
        help="Input grammar to fuzz",
    )

    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=50,
        help="Number of fuzzing payloads to generate",
    )

    parser.add_argument(
        "--method",
        choices=["GET", "POST", "PUT", "PATCH"],
        default="POST",
        help="HTTP method to use",
    )

    parser.add_argument(
        "--field",
        default="email",
        help="Request field name to fuzz for JSON/form/query bodies",
    )

    parser.add_argument(
        "--body-format",
        choices=["json", "form", "query", "raw"],
        default="json",
        help="How to place payloads in requests",
    )

    parser.add_argument(
        "--target-type",
        choices=["generic", "ghost", "prestashop"],
        default="generic",
        help=(
            "Target adapter. Ghost wraps JSON as {'data': {...}}; "
            "generic/prestashop use direct fields."
        ),
    )

    parser.add_argument(
        "--upload-field",
        default="file",
        help="Multipart field name for upload fuzzing",
    )

    parser.add_argument(
        "--header",
        action="append",
        default=[],
        help="Extra HTTP header, e.g. --header 'X-API-Key: secret'. Can be repeated.",
    )

    parser.add_argument(
        "--bearer-token",
        default=None,
        help="Bearer token for Authorization header",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Per-request timeout in seconds",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=1337,
        help="Random seed for reproducible fuzzing",
    )

    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification",
    )

    parser.add_argument(
        "--csv",
        default="results/fuzz_results.csv",
        help="CSV output path",
    )

    parser.add_argument(
        "--json-summary",
        default="results/fuzz_summary.json",
        help="JSON summary output path",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated payloads without sending HTTP requests",
    )

    parser.add_argument(
    "--extra-field",
    action="append",
    default=[],
    help="Extra form field in key=value format"
)

    return parser.parse_args()