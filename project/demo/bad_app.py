from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


SERVER_WEAK_EMAIL_REGEX = re.compile(r"^.+@.+$")


class DemoHandler(BaseHTTPRequestHandler):
    def send_json(self, status: int, body: dict) -> None:
        encoded = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.wfile.write(encoded)

    def read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))

        if length:
            return self.rfile.read(length)

        return b""

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/registration":
            raw = self.read_body()
            data = {}

            content_type = self.headers.get("Content-Type", "")

            if "application/json" in content_type:
                try:
                    data = json.loads(raw.decode("utf-8"))
                except json.JSONDecodeError:
                    return self.send_json(
                        400,
                        {
                            "ok": False,
                            "error": "bad json",
                        },
                    )

            elif "application/x-www-form-urlencoded" in content_type:
                data = {
                    key: value[0]
                    for key, value in parse_qs(raw.decode("utf-8")).items()
                }

            email = str(data.get("email", ""))

            # Deliberately weak server-side validation.
            # This models a client/server validation disagreement.
            if SERVER_WEAK_EMAIL_REGEX.match(email):
                return self.send_json(
                    201,
                    {
                        "ok": True,
                        "accepted_by": "weak-server",
                        "email": email,
                    },
                )

            return self.send_json(
                422,
                {
                    "ok": False,
                    "error": "invalid email",
                },
            )

        if parsed.path == "/upload":
            content_type = self.headers.get("Content-Type", "")

            if "multipart/form-data" not in content_type:
                return self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": "expected multipart",
                    },
                )

            # Minimal demo behavior:
            # accept if multipart reaches server.
            # This intentionally models weak upload validation.
            return self.send_json(
                201,
                {
                    "ok": True,
                    "accepted_by": "weak-upload-server",
                },
            )

        return self.send_json(
            404,
            {
                "ok": False,
                "error": "not found",
            },
        )

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path != "/search":
            return self.send_json(
                404,
                {
                    "ok": False,
                    "error": "not found",
                },
            )

        params = parse_qs(parsed.query)

        page = params.get("page", ["1"])[0]
        query = params.get("q", [""])[0]

        try:
            page_int = int(page)
        except ValueError:
            return self.send_json(
                422,
                {
                    "ok": False,
                    "error": "page must be integer",
                },
            )

        # Deliberately missing lower/upper bound checks.
        return self.send_json(
            200,
            {
                "ok": True,
                "page": page_int,
                "q": query,
            },
        )


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8099), DemoHandler)
    print("Demo target running on http://127.0.0.1:8099")
    server.serve_forever()