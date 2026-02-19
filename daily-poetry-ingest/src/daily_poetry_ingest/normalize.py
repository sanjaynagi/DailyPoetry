"""Normalization helpers for PoetryDB records.

This module defines canonical transformation rules used by the ingestion
pipeline and exercised by tests.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NormalizedPoem:
    """Canonical poem representation emitted by the normalizer."""

    title: str
    author: str
    text: str
    linecount: int
    content_hash: str
    source: str = "poetrydb"


@dataclass(frozen=True, slots=True)
class NormalizationError:
    """Describes why an input record could not be normalized."""

    reason: str
    input_record: dict


def _clean_line(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("line is not a string")
    return value.rstrip()


def canonical_text(lines: list[object]) -> str:
    """Build canonical poem text while preserving stanza breaks.

    - Keeps blank lines between stanzas.
    - Trims right-side whitespace on each line.
    - Removes trailing blank lines at EOF.
    """

    cleaned = [_clean_line(line) for line in lines]
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned)


def compute_content_hash(text: str) -> str:
    """Return deterministic hash for deduplication."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_record(record: dict) -> NormalizedPoem | NormalizationError:
    """Normalize a raw PoetryDB record into a canonical shape."""

    title = record.get("title")
    author = record.get("author")
    lines = record.get("lines")

    if not isinstance(title, str) or not title.strip():
        return NormalizationError(reason="missing_title", input_record=record)
    if not isinstance(author, str) or not author.strip():
        return NormalizationError(reason="missing_author", input_record=record)
    if not isinstance(lines, list) or not lines:
        return NormalizationError(reason="missing_lines", input_record=record)

    try:
        text = canonical_text(lines)
    except ValueError:
        return NormalizationError(reason="invalid_line_type", input_record=record)

    if not text:
        return NormalizationError(reason="empty_text", input_record=record)

    linecount = text.count("\n") + 1
    return NormalizedPoem(
        title=title.strip(),
        author=author.strip(),
        text=text,
        linecount=linecount,
        content_hash=compute_content_hash(text),
    )
