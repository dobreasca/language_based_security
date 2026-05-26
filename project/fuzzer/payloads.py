from __future__ import annotations
from .grammar import is_valid_for_mode
import random
import string
from typing import List

from .models import Payload


EMAIL_VALID = [
    "alice@example.com",
    "a.b+tag@example.co.uk",
    "user_name-123@sub.domain.org",
    "x@y.io",
    "firstname.lastname@university.edu",
]


EMAIL_INVALID_GRAMMAR_AWARE = [
    "plainaddress",
    "@missing-local.org",
    "missing-at.example.org",
    "user@",
    "user@example",
    "user@example..com",
    "user..dot@example.com",
    ".leadingdot@example.com",
    "trailingdot.@example.com",
    "user@-example.com",
    "user@example-.com",
    "user@example.com ",
    " user@example.com",
    "user@example.com\nBCC: victim@example.com",
    "user@example.com\r\nX-Injected: yes",
    "user\u0000@example.com",
    "üñîçøðé@example.com",
    "user@例え.テスト",
    "\"quoted local\"@example.com",
    "verylonglocalpart" * 8 + "@example.com",
    "user@" + ("a" * 70) + ".com",
]


PARAM_VALID = [
    "page=1",
    "limit=10",
    "sort=name:asc",
    "filter[email]=alice@example.com",
    "q=hello-world",
    "id=123",
]


PARAM_INVALID_GRAMMAR_AWARE = [
    "page=-1",
    "page=0",
    "page=999999999999999999999999",
    "limit=NaN",
    "limit=1e309",
    "id=abc",
    "id=../etc/passwd",
    "q=%00",
    "q=hello%0d%0aInjected:true",
    "q=<script>alert(1)</script>",
    "filter[email]=not-an-email",
    "filter[$where]=this.password!=null",
    "populate=*",
    "sort=../../name",
    "[]=x",
    "a[b][c][d][e][f]=deep",
]


UPLOAD_VALID = [
    ("avatar.png", "image/png", b"\x89PNG\r\n\x1a\nminimal"),
    ("document.txt", "text/plain", b"hello world"),
    ("profile.jpg", "image/jpeg", b"\xff\xd8\xff\xe0minimal"),
]


UPLOAD_INVALID_GRAMMAR_AWARE = [
    ("../../etc/passwd", "text/plain", b"root:x:0:0"),
    ("shell.php", "image/png", b"<?php echo 'owned'; ?>"),
    ("image.png.php", "image/png", b"<?php echo 'owned'; ?>"),
    ("nullbyte.png\x00.php", "image/png", b"fake"),
    ("huge-name-" + "a" * 240 + ".txt", "text/plain", b"x"),
    ("svg-script.svg", "image/svg+xml", b"<svg><script>alert(1)</script></svg>"),
    ("empty.txt", "text/plain", b""),
    ("wrong-mime.jpg", "application/x-msdownload", b"MZfake"),
]


def random_ascii(rng: random.Random, min_len: int = 1, max_len: int = 40) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation + " \t\n\r"
    length = rng.randint(min_len, max_len)
    result = ""

    for _ in range(length):
        result += rng.choice(alphabet)

    return result


def random_blackbox_payloads(
    mode: str,
    count: int,
    rng: random.Random,
) -> List[Payload]:
    payloads: List[Payload] = []

    for _ in range(count):
        value = random_ascii(rng)
        payloads.append(
            Payload(
                value=value,
                mode=mode,
                expected_valid=False,
                strategy="blackbox-random",
                description="Random ASCII payload baseline",
            )
        )

    return payloads


def generate_email_payloads(
    count: int,
    rng: random.Random,
    include_valid: bool = True,
) -> List[Payload]:
    candidates: List[Payload] = []

    if include_valid:
        for value in EMAIL_VALID:
            candidates.append(
                Payload(
                    value=value,
                    mode="email",
                    expected_valid=is_valid_for_mode("email", value),
                    strategy="grammar-valid",
                    description="Valid email according to the regex grammar",
                )
            )

    for value in EMAIL_INVALID_GRAMMAR_AWARE:
        candidates.append(
            Payload(
                value=value,
                mode="email",
                expected_valid=is_valid_for_mode("email", value),
                strategy="grammar-mutated-invalid",
                description="Email grammar boundary or parser disagreement case",
            )
        )

    random_count = count // 5
    if random_count < 2:
        random_count = 2

    candidates.extend(random_blackbox_payloads("email", random_count, rng))

    return sample_or_extend(candidates, count, rng)


def generate_param_payloads(
    count: int,
    rng: random.Random,
    include_valid: bool = True,
) -> List[Payload]:
    candidates: List[Payload] = []

    if include_valid:
        for value in PARAM_VALID:
            candidates.append(
                Payload(
                    value=value,
                    mode="params",
                    expected_valid=is_valid_for_mode("params", value),
                    strategy="grammar-valid",
                    description="Valid HTTP query parameter pattern",
                )
            )

    for value in PARAM_INVALID_GRAMMAR_AWARE:
        candidates.append(
            Payload(
                value=value,
                mode="params",
                expected_valid=is_valid_for_mode("params", value),
                strategy="grammar-mutated-invalid",
                description="HTTP parameter grammar edge case",
            )
        )

    random_count = count // 5
    if random_count < 2:
        random_count = 2

    candidates.extend(random_blackbox_payloads("params", random_count, rng))

    return sample_or_extend(candidates, count, rng)


def generate_upload_payloads(
    count: int,
    rng: random.Random,
    include_valid: bool = True,
) -> List[Payload]:
    candidates: List[Payload] = []

    if include_valid:
        for name, mime, content in UPLOAD_VALID:
            candidates.append(
                Payload(
                    value=name,
                    mode="upload",
                    expected_valid=is_valid_for_mode("upload", name),
                    strategy="grammar-valid",
                    description=f"Valid-looking upload filename and MIME type {mime}",
                    metadata={
                        "filename": name,
                        "mime_type": mime,
                        "content": content.hex(),
                    },
                )
            )

    for name, mime, content in UPLOAD_INVALID_GRAMMAR_AWARE:
        candidates.append(
            Payload(
                value=name,
                mode="upload",
                expected_valid=is_valid_for_mode("upload", name),
                strategy="grammar-mutated-invalid",
                description=f"Upload boundary case with MIME type {mime}",
                metadata={
                    "filename": name,
                    "mime_type": mime,
                    "content": content.hex(),
                },
            )
        )

    return sample_or_extend(candidates, count, rng)


def sample_or_extend(
    candidates: List[Payload],
    count: int,
    rng: random.Random,
) -> List[Payload]:
    if count <= len(candidates):
        chosen = candidates[:]
        rng.shuffle(chosen)
        return chosen[:count]

    result = candidates[:]

    while len(result) < count:
        base = rng.choice(candidates)
        suffix = random_ascii(rng, 1, 8)

        result.append(
            Payload(
                value=f"{base.value}{suffix}",
                mode=base.mode,
                expected_valid=base.expected_valid,
                strategy=base.strategy + "+random-suffix",
                description=base.description,
                metadata=base.metadata,
            )
        )

    rng.shuffle(result)
    return result


def generate_payloads(
    mode: str,
    count: int,
    seed: int | None = None,
    include_valid: bool = True,
) -> List[Payload]:
    rng = random.Random(seed)

    if mode == "email":
        return generate_email_payloads(count, rng, include_valid)

    if mode == "params":
        return generate_param_payloads(count, rng, include_valid)

    if mode == "upload":
        return generate_upload_payloads(count, rng, include_valid)

    raise ValueError(f"Unsupported mode: {mode}")