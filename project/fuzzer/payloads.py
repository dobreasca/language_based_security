from __future__ import annotations

from .grammar import is_valid_for_mode, is_valid_upload_payload
import random
import string
import base64
from typing import List

from .models import Payload

TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)

TINY_JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAEDAQE/ASP/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/ASP/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAY/Al//xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/IV//2gAMAwEAAgADAAAAEP/EFBQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QH//EFBQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQIBAT8QH//EFBABAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEAAT8QH//Z"
)

TINY_WEBP = base64.b64decode(
    "UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA"
)

def random_ascii(rng: random.Random, min_len: int = 1, max_len: int = 40) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation + " \t\n\r"
    length = rng.randint(min_len, max_len)

    result = ""
    for _ in range(length):
        result += rng.choice(alphabet)

    return result


def random_label(rng: random.Random, min_len: int = 1, max_len: int = 12) -> str:
    alphabet = string.ascii_lowercase + string.digits
    length = rng.randint(min_len, max_len)

    result = ""
    for _ in range(length):
        result += rng.choice(alphabet)

    return result


def random_local_part(rng: random.Random, min_len: int = 1, max_len: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "._%+-"
    length = rng.randint(min_len, max_len)

    result = ""
    for _ in range(length):
        result += rng.choice(alphabet)

    result = result.strip(".")
    result = result.replace("..", ".")

    if result == "":
        result = "user"

    return result


def generate_random_valid_email(rng: random.Random) -> str:
    local = random_local_part(rng)
    domain = random_label(rng)
    tld = rng.choice(["com", "org", "net", "edu", "io", "se", "co.uk"])

    if tld == "co.uk":
        return f"{local}@{domain}.co.uk"

    return f"{local}@{domain}.{tld}"


def generate_random_invalid_email(rng: random.Random) -> str:
    valid = generate_random_valid_email(rng)

    mutations = [
        lambda email: email.replace("@", "", 1),
        lambda email: "@" + email,
        lambda email: email.split("@")[0] + "@",
        lambda email: email.split("@")[0] + "@example",
        lambda email: email.replace(".", "..", 1),
        lambda email: "." + email,
        lambda email: email + " ",
        lambda email: " " + email,
        lambda email: email + "\nBCC: victim@example.com",
        lambda email: email + "\r\nX-Test: injected",
        lambda email: email.replace("@", "\u0000@", 1),
        lambda email: email.replace("@", "@-", 1),
        lambda email: "a" * rng.randint(80, 200) + "@example.com",
        lambda email: random_ascii(rng, 1, 40),
    ]

    mutation = rng.choice(mutations)
    return mutation(valid)

def random_param_key(rng: random.Random) -> str:
    first = string.ascii_letters + "_"
    rest = string.ascii_letters + string.digits + "_"

    length = rng.randint(1, 15)
    key = rng.choice(first)

    for _ in range(length - 1):
        key += rng.choice(rest)

    return key


def random_param_value(rng: random.Random) -> str:
    alphabet = string.ascii_letters + string.digits + "._~%+-:@,"
    length = rng.randint(0, 30)

    value = ""
    for _ in range(length):
        value += rng.choice(alphabet)

    return value


def generate_random_valid_param(rng: random.Random) -> str:
    key = random_param_key(rng)

    value_type = rng.choice(["integer", "word", "email", "sort", "slug"])

    if value_type == "integer":
        value = str(rng.randint(1, 500))

    elif value_type == "email":
        value = generate_random_valid_email(rng)

    elif value_type == "sort":
        field = rng.choice(["name", "price", "date", "id", "title"])
        direction = rng.choice(["asc", "desc"])
        value = f"{field}:{direction}"

    elif value_type == "slug":
        words = []
        for _ in range(rng.randint(1, 4)):
            words.append(random_label(rng, 2, 8))
        value = "-".join(words)

    else:
        value = random_param_value(rng)

    return f"{key}={value}"


def generate_random_invalid_param(rng: random.Random) -> str:
    valid = generate_random_valid_param(rng)

    mutations = [
        lambda param: param.replace("=", "", 1),
        lambda param: "=" + param,
        lambda param: param + "\r\nX-Test: injected",
        lambda param: param.split("=")[0] + "=../etc/passwd",
        lambda param: param.split("=")[0] + "=<script>alert(1)</script>",
        lambda param: param.split("=")[0] + "=%00",
        lambda param: param.split("=")[0] + "=1e309",
        lambda param: param.split("=")[0] + "=NaN",
        lambda param: param.split("=")[0] + "=-1",
        lambda param: "[]=x",
        lambda param: "a[b][c][d][e][f]=deep",
        lambda param: "filter[$where]=this.password!=null",
        lambda param: "sort=../../name",
        lambda param: random_ascii(rng, 1, 50),
    ]

    mutation = rng.choice(mutations)
    return mutation(valid)

def random_safe_filename(rng: random.Random) -> str:
    alphabet = string.ascii_letters + string.digits + "._-"
    length = rng.randint(3, 20)

    base = ""
    for _ in range(length):
        base += rng.choice(alphabet)

    base = base.strip(".")

    if base == "":
        base = "file"

    extension = rng.choice(["txt", "png", "jpg", "jpeg", "webp", "pdf"])

    return f"{base}.{extension}"


def fake_content_for_filename(filename: str) -> tuple[str, bytes]:
    lowered = filename.lower()

    if lowered.endswith(".png"):
        return "image/png", TINY_PNG

    if lowered.endswith(".jpg") or lowered.endswith(".jpeg"):
        return "image/jpeg", TINY_JPEG

    if lowered.endswith(".webp"):
        return "image/webp", TINY_WEBP

    if lowered.endswith(".pdf"):
        return "application/pdf", b"%PDF-1.4\nminimal-pdf"

    return "text/plain", b"hello world"


def generate_random_valid_upload(rng: random.Random) -> tuple[str, str, bytes]:
    filename = random_safe_filename(rng)
    mime, content = fake_content_for_filename(filename)
    return filename, mime, content


def generate_random_invalid_upload(rng: random.Random) -> tuple[str, str, bytes]:
    valid_name = random_safe_filename(rng)

    mutations = [
        lambda name: ("../" + name, "text/plain", b"path traversal"),
        lambda name: ("../../etc/passwd", "text/plain", b"root:x:0:0"),
        lambda name: ("shell.php", "image/png", b"<?php echo 'owned'; ?>"),
        lambda name: (name + ".php", "image/png", b"<?php echo 'owned'; ?>"),
        lambda name: ("nullbyte.png\x00.php", "image/png", b"fake"),
        lambda name: ("svg-script.svg", "image/svg+xml", b"<svg><script>alert(1)</script></svg>"),
        lambda name: ("huge-" + ("a" * rng.randint(120, 260)) + ".txt", "text/plain", b"x"),
        lambda name: ("wrong-mime.jpg", "application/x-msdownload", b"MZfake"),
        lambda name: ("empty.png", "image/png", b""),
        lambda name: ("file with spaces.png", "image/png", b"\x89PNG\r\n\x1a\nfake"),
        lambda name: ("unicode-例.png", "image/png", b"\x89PNG\r\n\x1a\nfake"),
        lambda name: ("noextension", "application/octet-stream", b"raw"),
        lambda name: (random_ascii(rng, 1, 40), "application/octet-stream", b"random"),
    ]

    mutation = rng.choice(mutations)
    return mutation(valid_name)

def random_ghost_image_filename(rng: random.Random) -> str:
    alphabet = string.ascii_letters + string.digits + "._-"
    length = rng.randint(3, 20)

    base = ""
    for _ in range(length):
        base += rng.choice(alphabet)

    base = base.strip("._-")

    if base == "":
        base = "image"

    extension = rng.choice(["png", "jpg", "jpeg", "webp"])

    return f"{base}.{extension}"


def generate_random_valid_ghost_upload(rng: random.Random) -> tuple[str, str, bytes]:
    filename = random_ghost_image_filename(rng)
    mime, content = fake_content_for_filename(filename)
    return filename, mime, content


def generate_random_invalid_ghost_upload(rng: random.Random) -> tuple[str, str, bytes]:
    valid_name = random_ghost_image_filename(rng)

    mutations = [
        lambda name: ("../" + name, "image/png", TINY_PNG),
        lambda name: ("../../etc/passwd", "text/plain", b"root:x:0:0"),
        lambda name: ("shell.php", "image/png", b"<?php echo 'owned'; ?>"),
        lambda name: (name + ".php", "image/png", b"<?php echo 'owned'; ?>"),
        lambda name: ("nullbyte.png\x00.php", "image/png", TINY_PNG),
        lambda name: ("svg-script.svg", "image/svg+xml", b"<svg><script>alert(1)</script></svg>"),
        lambda name: ("wrong-mime.jpg", "application/x-msdownload", b"MZfake"),
        lambda name: ("fake-image.png", "image/png", b"not really a png"),
        lambda name: ("fake-image.jpg", "image/jpeg", b"not really a jpeg"),
        lambda name: ("empty.png", "image/png", b""),
        lambda name: ("document.txt", "text/plain", b"hello world"),
        lambda name: ("file with spaces.png", "image/png", TINY_PNG),
        lambda name: ("unicode-例.png", "image/png", TINY_PNG),
        lambda name: ("huge-" + ("a" * rng.randint(120, 260)) + ".png", "image/png", TINY_PNG),
    ]

    mutation = rng.choice(mutations)
    return mutation(valid_name)

GHOST_UPLOAD_VALID = [
    ("ghost-image.png", "image/png", TINY_PNG),
    ("ghost-photo.jpg", "image/jpeg", TINY_JPEG),
    ("ghost-cover.webp", "image/webp", TINY_WEBP),
]


GHOST_UPLOAD_INVALID = [
    ("shell.php", "image/png", b"<?php echo 'owned'; ?>"),
    ("image.png.php", "image/png", b"<?php echo 'owned'; ?>"),
    ("nullbyte.png\x00.php", "image/png", TINY_PNG),
    ("document.txt", "text/plain", b"hello world"),
    ("fake-image.png", "image/png", b"not really a png"),
    ("wrong-mime.jpg", "application/x-msdownload", b"MZfake"),
    ("svg-script.svg", "image/svg+xml", b"<svg><script>alert(1)</script></svg>"),
    ("../../etc/passwd", "text/plain", b"root:x:0:0"),
]

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



def random_blackbox_payloads(
    mode: str,
    count: int,
    rng: random.Random,
) -> List[Payload]:
    payloads: List[Payload] = []

    for _ in range(count):
        value = random_ascii(rng)

        if mode == "upload":
            expected = False
        else:
            expected = is_valid_for_mode(mode, value)

        payloads.append(
            Payload(
                value=value,
                mode=mode,
                expected_valid=expected,
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
                    strategy="grammar-valid-seed",
                    description="Seed valid email checked against regex grammar",
                )
            )

    for value in EMAIL_INVALID_GRAMMAR_AWARE:
        candidates.append(
            Payload(
                value=value,
                mode="email",
                expected_valid=is_valid_for_mode("email", value),
                strategy="grammar-mutated-seed",
                description="Seed email boundary case checked against regex grammar",
            )
        )

    generated_valid_count = count // 3
    generated_invalid_count = count // 3

    if generated_valid_count < 1:
        generated_valid_count = 1

    if generated_invalid_count < 1:
        generated_invalid_count = 1

    if include_valid:
        for _ in range(generated_valid_count):
            value = generate_random_valid_email(rng)
            candidates.append(
                Payload(
                    value=value,
                    mode="email",
                    expected_valid=is_valid_for_mode("email", value),
                    strategy="grammar-generated-valid",
                    description="Random valid email generated from grammar components",
                )
            )

    for _ in range(generated_invalid_count):
        value = generate_random_invalid_email(rng)
        candidates.append(
            Payload(
                value=value,
                mode="email",
                expected_valid=is_valid_for_mode("email", value),
                strategy="grammar-generated-invalid",
                description="Random invalid email generated by grammar-aware mutation",
            )
        )

    blackbox_count = count // 5
    if blackbox_count < 2:
        blackbox_count = 2

    candidates.extend(random_blackbox_payloads("email", blackbox_count, rng))

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
                    strategy="grammar-valid-seed",
                    description="Seed valid HTTP parameter checked against regex grammar",
                )
            )

    for value in PARAM_INVALID_GRAMMAR_AWARE:
        candidates.append(
            Payload(
                value=value,
                mode="params",
                expected_valid=is_valid_for_mode("params", value),
                strategy="grammar-mutated-seed",
                description="Seed HTTP parameter boundary case checked against regex grammar",
            )
        )

    generated_valid_count = count // 3
    generated_invalid_count = count // 3

    if generated_valid_count < 1:
        generated_valid_count = 1

    if generated_invalid_count < 1:
        generated_invalid_count = 1

    if include_valid:
        for _ in range(generated_valid_count):
            value = generate_random_valid_param(rng)
            candidates.append(
                Payload(
                    value=value,
                    mode="params",
                    expected_valid=is_valid_for_mode("params", value),
                    strategy="grammar-generated-valid",
                    description="Random valid HTTP parameter generated from grammar components",
                )
            )

    for _ in range(generated_invalid_count):
        value = generate_random_invalid_param(rng)
        candidates.append(
            Payload(
                value=value,
                mode="params",
                expected_valid=is_valid_for_mode("params", value),
                strategy="grammar-generated-invalid",
                description="Random invalid HTTP parameter generated by grammar-aware mutation",
            )
        )

    blackbox_count = count // 5
    if blackbox_count < 2:
        blackbox_count = 2

    candidates.extend(random_blackbox_payloads("params", blackbox_count, rng))

    return sample_or_extend(candidates, count, rng)

def generate_ghost_upload_payloads(
    count: int,
    rng: random.Random,
    include_valid: bool = True,
) -> List[Payload]:
    candidates: List[Payload] = []

    if include_valid:
        for name, mime, content in GHOST_UPLOAD_VALID:
            candidates.append(
                Payload(
                    value=name,
                    mode="upload",
                    expected_valid=is_valid_upload_payload(name, mime, content),
                    strategy="ghost-valid-seed",
                    description=f"Ghost valid image upload seed; MIME type {mime}",
                    metadata={
                        "filename": name,
                        "mime_type": mime,
                        "content": content.hex(),
                    },
                )
            )

    for name, mime, content in GHOST_UPLOAD_INVALID:
        candidates.append(
            Payload(
                value=name,
                mode="upload",
                expected_valid=is_valid_upload_payload(name, mime, content),
                strategy="ghost-invalid-seed",
                description=f"Ghost invalid image upload seed; MIME type {mime}",
                metadata={
                    "filename": name,
                    "mime_type": mime,
                    "content": content.hex(),
                },
            )
        )

    generated_valid_count = count // 3
    generated_invalid_count = count // 3

    if generated_valid_count < 1:
        generated_valid_count = 1

    if generated_invalid_count < 1:
        generated_invalid_count = 1

    if include_valid:
        for _ in range(generated_valid_count):
            name, mime, content = generate_random_valid_ghost_upload(rng)
            candidates.append(
                Payload(
                    value=name,
                    mode="upload",
                    expected_valid=is_valid_upload_payload(name, mime, content),
                    strategy="ghost-generated-valid",
                    description=f"Random valid Ghost image upload; MIME type {mime}",
                    metadata={
                        "filename": name,
                        "mime_type": mime,
                        "content": content.hex(),
                    },
                )
            )

    for _ in range(generated_invalid_count):
        name, mime, content = generate_random_invalid_ghost_upload(rng)
        candidates.append(
            Payload(
                value=name,
                mode="upload",
                expected_valid=is_valid_upload_payload(name, mime, content),
                strategy="ghost-generated-invalid",
                description=f"Random invalid Ghost image upload; MIME type {mime}",
                metadata={
                    "filename": name,
                    "mime_type": mime,
                    "content": content.hex(),
                },
            )
        )

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
                    strategy="grammar-valid-seed",
                    description=f"Seed valid upload filename checked against regex grammar; MIME type {mime}",
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
                strategy="grammar-mutated-seed",
                description=f"Seed upload boundary case checked against regex grammar; MIME type {mime}",
                metadata={
                    "filename": name,
                    "mime_type": mime,
                    "content": content.hex(),
                },
            )
        )

    generated_valid_count = count // 3
    generated_invalid_count = count // 3

    if generated_valid_count < 1:
        generated_valid_count = 1

    if generated_invalid_count < 1:
        generated_invalid_count = 1

    if include_valid:
        for _ in range(generated_valid_count):
            name, mime, content = generate_random_valid_upload(rng)
            candidates.append(
                Payload(
                    value=name,
                    mode="upload",
                    expected_valid=is_valid_upload_payload(name, mime, content),
                    strategy="grammar-generated-valid",
                    description=f"Random valid upload generated from filename grammar; MIME type {mime}",
                    metadata={
                        "filename": name,
                        "mime_type": mime,
                        "content": content.hex(),
                    },
                )
            )

    for _ in range(generated_invalid_count):
        name, mime, content = generate_random_invalid_upload(rng)
        candidates.append(
            Payload(
                value=name,
                mode="upload",
                expected_valid=is_valid_upload_payload(name, mime, content),
                strategy="grammar-generated-invalid",
                description=f"Random invalid upload generated by grammar-aware mutation; MIME type {mime}",
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

        if base.mode == "upload":
            name, mime, content = generate_random_invalid_upload(rng)
            result.append(
                Payload(
                    value=name,
                    mode="upload",
                    expected_valid=is_valid_upload_payload(name, mime, content),
                    strategy=base.strategy + "+generated-extra",
                    description="Extra generated upload payload",
                    metadata={
                        "filename": name,
                        "mime_type": mime,
                        "content": content.hex(),
                    },
                )
            )

        elif base.mode == "email":
            value = generate_random_invalid_email(rng)
            result.append(
                Payload(
                    value=value,
                    mode="email",
                    expected_valid=is_valid_for_mode("email", value),
                    strategy=base.strategy + "+generated-extra",
                    description="Extra generated email payload",
                    metadata=base.metadata,
                )
            )

        elif base.mode == "params":
            value = generate_random_invalid_param(rng)
            result.append(
                Payload(
                    value=value,
                    mode="params",
                    expected_valid=is_valid_for_mode("params", value),
                    strategy=base.strategy + "+generated-extra",
                    description="Extra generated HTTP parameter payload",
                    metadata=base.metadata,
                )
            )

        else:
            suffix = random_ascii(rng, 1, 8)
            new_value = f"{base.value}{suffix}"

            result.append(
                Payload(
                    value=new_value,
                    mode=base.mode,
                    expected_valid=is_valid_for_mode(base.mode, new_value),
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
    target_type: str = "generic",
) -> List[Payload]:
    rng = random.Random(seed)

    if mode == "email":
        return generate_email_payloads(count, rng, include_valid)

    if mode == "params":
        return generate_param_payloads(count, rng, include_valid)

    if mode == "upload":
        if target_type == "ghost":
            return generate_ghost_upload_payloads(count, rng, include_valid)

        return generate_upload_payloads(count, rng, include_valid)

    raise ValueError(f"Unsupported mode: {mode}")