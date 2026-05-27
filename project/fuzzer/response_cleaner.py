from __future__ import annotations

import re
from html import unescape


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_html_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    return collapse_whitespace(text)


def remove_invisible_or_irrelevant_blocks(html: str) -> str:

    patterns = [
        r"<script[\s\S]*?</script>",
        r"<style[\s\S]*?</style>",
        r"<template[\s\S]*?</template>",
        r"<noscript[\s\S]*?</noscript>",
        r"<svg[\s\S]*?</svg>",
    ]

    cleaned = html

    for pattern in patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    return cleaned


def remove_hidden_elements(html: str) -> str:

    patterns = [
        r"<[^>]*(?:class=[\"'][^\"']*(?:d-none|hidden|visually-hidden)[^\"']*[\"'])[^>]*>[\s\S]*?</[^>]+>",
        r"<[^>]*(?:aria-hidden=[\"']true[\"'])[^>]*>[\s\S]*?</[^>]+>",
        r"<[^>]*(?:style=[\"'][^\"']*display\s*:\s*none[^\"']*[\"'])[^>]*>[\s\S]*?</[^>]+>",
        r"<[^>]*(?:hidden)[^>]*>[\s\S]*?</[^>]+>",
    ]

    cleaned = html

    for pattern in patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    return cleaned


def extract_alert_blocks(html: str) -> str:

    patterns = [
        r"<[^>]*role=[\"']alert[\"'][^>]*>[\s\S]*?</[^>]+>",
        r"<[^>]*class=[\"'][^\"']*(?:alert|error|errors|success|warning|notice|notification|message|messages|form-error|help-block)[^\"']*[\"'][^>]*>[\s\S]*?</[^>]+>",
        r"<[^>]*id=[\"'][^\"']*(?:alert|error|errors|success|warning|notice|notification|message|messages)[^\"']*[\"'][^>]*>[\s\S]*?</[^>]+>",
    ]

    matches: list[str] = []

    for pattern in patterns:
        matches.extend(re.findall(pattern, html, flags=re.IGNORECASE))

    if matches:
        return " ".join(matches)

    return ""


def extract_region_around_field(html: str, field: str) -> str:

    if not field:
        return ""

    escaped_field = re.escape(field)

    field_patterns = [
        rf"name=[\"']{escaped_field}[\"']",
        rf"id=[\"']{escaped_field}[\"']",
        rf"data-[^=]+=[\"']{escaped_field}[\"']",
    ]

    field_match = None

    for pattern in field_patterns:
        field_match = re.search(pattern, html, flags=re.IGNORECASE)
        if field_match:
            break

    if not field_match:
        return ""

    position = field_match.start()

    form_start = html.rfind("<form", 0, position)
    form_end = html.find("</form>", position)

    if form_start != -1 and form_end != -1:
        return html[form_start : form_end + len("</form>")]

    section_start = html.rfind("<section", 0, position)
    section_end = html.find("</section>", position)

    if section_start != -1 and section_end != -1:
        return html[section_start : section_end + len("</section>")]

    start = max(0, position - 3000)
    end = min(len(html), position + 3000)

    return html[start:end]


def extract_region_by_keywords(html: str, keywords: list[str]) -> str:

    lowered = html.lower()

    for keyword in keywords:
        pos = lowered.find(keyword.lower())

        if pos == -1:
            continue

        section_start = html.rfind("<section", 0, pos)
        section_end = html.find("</section>", pos)

        if section_start != -1 and section_end != -1:
            return html[section_start : section_end + len("</section>")]

        form_start = html.rfind("<form", 0, pos)
        form_end = html.find("</form>", pos)

        if form_start != -1 and form_end != -1:
            return html[form_start : form_end + len("</form>")]

        start = max(0, pos - 3000)
        end = min(len(html), pos + 3000)

        return html[start:end]

    return ""


def choose_relevant_region(
    html: str,
    target_type: str = "generic",
    mode: str = "",
    field: str = "",
) -> str:

    field_region = extract_region_around_field(html, field)

    if field_region:
        field_alerts = extract_alert_blocks(field_region)

        if field_alerts:
            return field_alerts

        return field_region

    target_keywords = []

    if target_type == "prestashop":
        target_keywords = [
            "newsletter",
            "subscription",
            "emailsubscription",
            "contact",
            "search",
            "cart",
            "registration",
        ]

    elif target_type == "ghost":
        target_keywords = [
            "member",
            "signup",
            "sign in",
            "magic link",
            "post",
            "tag",
            "upload",
            "slug",
        ]

    keyword_region = extract_region_by_keywords(html, target_keywords)

    if keyword_region:
        keyword_alerts = extract_alert_blocks(keyword_region)

        if keyword_alerts:
            return keyword_alerts

        return keyword_region

    all_alerts = extract_alert_blocks(html)

    if all_alerts:
        return all_alerts

    return html


def clean_response_for_classification(
    html: str,
    target_type: str = "generic",
    mode: str = "",
    field: str = "",
) -> str:

    cleaned = remove_invisible_or_irrelevant_blocks(html)
    cleaned = remove_hidden_elements(cleaned)

    relevant = choose_relevant_region(
        cleaned,
        target_type=target_type,
        mode=mode,
        field=field,
    )

    return strip_html_tags(relevant)