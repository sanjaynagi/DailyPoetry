"""Author image enrichment utilities.

This module resolves image URLs for authors via Wikipedia APIs and produces
nullable image metadata records for ingestion artifacts.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AuthorImageRecord:
    """Represents image metadata for a single author."""

    name: str
    image_url: str | None
    image_source: str | None


def _fetch_json(url: str, timeout_seconds: float) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "daily-poetry-ingest/0.1"})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch_with_retry(url: str, timeout_seconds: float, retries: int, backoff_seconds: float) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return _fetch_json(url, timeout_seconds)
        except Exception as exc:  # pragma: no cover - network variability
            last_error = exc
            if attempt < retries:
                time.sleep(backoff_seconds * (2**attempt))
    assert last_error is not None
    raise last_error


def _extract_thumbnail(page: dict) -> str | None:
    thumbnail = page.get("thumbnail")
    if isinstance(thumbnail, dict):
        source = thumbnail.get("source")
        if isinstance(source, str) and source.strip():
            return source.strip()

    original = page.get("original")
    if isinstance(original, dict):
        source = original.get("source")
        if isinstance(source, str) and source.strip():
            return source.strip()

    return None


def resolve_author_image(
    author: str,
    timeout_seconds: float,
    retries: int,
    backoff_seconds: float,
) -> AuthorImageRecord:
    """Resolve an author image URL from Wikipedia, returning nullable metadata."""

    encoded = urllib.parse.quote(author, safe="")
    endpoint = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&prop=pageimages&format=json&piprop=thumbnail|original&pithumbsize=600&titles={encoded}"
    )

    try:
        payload = _fetch_with_retry(endpoint, timeout_seconds, retries, backoff_seconds)
    except Exception:
        return AuthorImageRecord(name=author, image_url=None, image_source=None)

    query = payload.get("query") if isinstance(payload, dict) else None
    pages = query.get("pages") if isinstance(query, dict) else None
    if not isinstance(pages, dict):
        return AuthorImageRecord(name=author, image_url=None, image_source=None)

    for page in pages.values():
        if not isinstance(page, dict):
            continue
        image_url = _extract_thumbnail(page)
        if image_url:
            return AuthorImageRecord(name=author, image_url=image_url, image_source="wikipedia")

    return AuthorImageRecord(name=author, image_url=None, image_source=None)


def enrich_authors(
    authors: list[str],
    timeout_seconds: float,
    retries: int,
    backoff_seconds: float,
    rate_limit_rps: float,
) -> tuple[list[dict], list[dict]]:
    """Enrich a sorted list of unique authors with nullable image metadata.

    Returns records and non-fatal errors.
    """

    records: list[dict] = []
    errors: list[dict] = []
    delay = 1.0 / rate_limit_rps if rate_limit_rps > 0 else 0.0

    for author in authors:
        try:
            record = resolve_author_image(author, timeout_seconds, retries, backoff_seconds)
            records.append(
                {
                    "name": record.name,
                    "image_url": record.image_url,
                    "image_source": record.image_source,
                }
            )
        except Exception as exc:  # pragma: no cover - defensive catch
            records.append({"name": author, "image_url": None, "image_source": None})
            errors.append({"kind": "author_image_error", "author": author, "reason": str(exc)})

        if delay > 0:
            time.sleep(delay)

    records.sort(key=lambda item: item["name"])
    return records, errors
