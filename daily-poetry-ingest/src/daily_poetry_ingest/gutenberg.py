"""Project Gutenberg ingestion helpers with strict poem extraction rules."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from daily_poetry_ingest.normalize import NormalizationError, NormalizedPoem, normalize_record

_START_MARKER_RE = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK", re.IGNORECASE)
_END_MARKER_RE = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK", re.IGNORECASE)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_MULTISPACE_RE = re.compile(r"\s+")
_WHITESPACE_LINE_RE = re.compile(r"^\s*$")
_HEADER_STOPWORDS = {
    "contents",
    "table of contents",
    "preface",
    "introduction",
    "appendix",
    "appendices",
    "notes",
    "footnotes",
    "bibliography",
}
_TITLE_REJECT_TERMS = (
    "collected",
    "anthology",
    "selection",
    "selected",
    "poems",
    "poetical works",
    "complete works",
    "works",
    "volume",
    "vol.",
)


@dataclass(frozen=True, slots=True)
class GutenbergCandidate:
    """Catalog entry eligible for strict poem extraction."""

    ebook_id: int
    title: str
    author: str
    language: str


def _normalize_token_string(value: str) -> str:
    collapsed = _NON_ALNUM_RE.sub(" ", value.casefold())
    return _MULTISPACE_RE.sub(" ", collapsed).strip()


def _parse_ebook_id(row: dict[str, str]) -> int | None:
    raw = (row.get("Text#") or row.get("Text") or "").strip()
    if not raw.isdigit():
        return None
    return int(raw)


def _row_contains_poetry_signal(row: dict[str, str]) -> bool:
    haystack = " ".join(
        [
            row.get("Subjects", ""),
            row.get("Bookshelves", ""),
            row.get("LoCC", ""),
        ]
    )
    normalized = _normalize_token_string(haystack)
    return "poetry" in normalized or "poem" in normalized


def _is_likely_single_poem_title(title: str) -> bool:
    lowered = title.casefold()
    return all(term not in lowered for term in _TITLE_REJECT_TERMS)


def load_catalog_candidates(catalog_path: Path, *, language: str = "en") -> tuple[list[GutenbergCandidate], list[dict]]:
    """Load strict poem candidates from Gutenberg metadata CSV."""

    candidates: list[GutenbergCandidate] = []
    errors: list[dict] = []

    with catalog_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=2):
            title = (row.get("Title") or "").strip()
            author = (row.get("Authors") or "").strip()
            row_language = (row.get("Language") or "").strip().casefold()
            row_type = (row.get("Type") or "").strip().casefold()
            ebook_id = _parse_ebook_id(row)

            if row_type != "text":
                continue
            if not title or not author or ebook_id is None:
                errors.append({"kind": "metadata_error", "line": index, "reason": "missing_required_fields"})
                continue
            if language and row_language != language.casefold():
                continue
            if not _row_contains_poetry_signal(row):
                continue
            if not _is_likely_single_poem_title(title):
                continue

            candidates.append(
                GutenbergCandidate(
                    ebook_id=ebook_id,
                    title=title,
                    author=author,
                    language=row_language or language,
                )
            )

    candidates.sort(key=lambda item: item.ebook_id)
    return candidates, errors


def _read_gutenberg_text(texts_dir: Path, ebook_id: int) -> str:
    """Load Gutenberg text from known cache layouts."""

    flat_names = (f"{ebook_id}.txt", f"pg{ebook_id}.txt", f"{ebook_id}-0.txt")
    nested_names = (f"pg{ebook_id}.txt", f"{ebook_id}.txt", f"{ebook_id}-0.txt")

    candidate_paths = [texts_dir / name for name in flat_names]
    candidate_paths.extend(texts_dir / str(ebook_id) / name for name in nested_names)
    candidate_paths.extend(texts_dir / "epub" / str(ebook_id) / name for name in nested_names)

    for path in candidate_paths:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    raise FileNotFoundError(f"No text file found for ebook_id={ebook_id}")


def _slice_between_markers(raw_text: str) -> str:
    start_match = _START_MARKER_RE.search(raw_text)
    end_match = _END_MARKER_RE.search(raw_text)

    start_index = start_match.end() if start_match else 0
    end_index = end_match.start() if end_match else len(raw_text)
    if start_index >= end_index:
        return raw_text
    return raw_text[start_index:end_index]


def _trim_front_matter(lines: list[str], title: str, author: str) -> list[str]:
    normalized_title = _normalize_token_string(title)
    normalized_author = _normalize_token_string(author)
    title_index = None

    for idx, line in enumerate(lines[:140]):
        normalized_line = _normalize_token_string(line)
        if not normalized_line:
            continue
        if normalized_line == normalized_title or normalized_title in normalized_line:
            title_index = idx
            break

    if title_index is not None:
        lines = lines[title_index + 1 :]

    while lines and _WHITESPACE_LINE_RE.match(lines[0]):
        lines = lines[1:]

    while lines:
        current = _normalize_token_string(lines[0])
        if not current:
            lines = lines[1:]
            continue
        if current.startswith("by ") or current == normalized_author:
            lines = lines[1:]
            continue
        break

    while lines and _WHITESPACE_LINE_RE.match(lines[0]):
        lines = lines[1:]
    return lines


def _trim_tail_sections(lines: list[str]) -> list[str]:
    cutoff = len(lines)
    for idx, line in enumerate(lines):
        normalized = _normalize_token_string(line)
        if not normalized:
            continue
        if normalized in _HEADER_STOPWORDS or normalized.startswith("chapter "):
            if idx >= 8:
                cutoff = idx
                break
    lines = lines[:cutoff]
    while lines and _WHITESPACE_LINE_RE.match(lines[-1]):
        lines.pop()
    return lines


def _is_strict_poem_shape(lines: list[str], *, max_non_empty_lines: int = 120) -> bool:
    non_empty = [line for line in lines if line.strip()]
    if len(non_empty) < 8 or len(non_empty) > max_non_empty_lines:
        return False

    text_length = sum(len(line) for line in non_empty)
    if text_length < 180 or text_length > 9000:
        return False

    short_lines = sum(1 for line in non_empty if len(line) <= 72)
    if short_lines / len(non_empty) < 0.9:
        return False

    if any(len(line) > 100 for line in non_empty):
        return False

    word_counts = [len(line.split()) for line in non_empty]
    if sum(1 for count in word_counts if count > 14) > max(1, len(word_counts) // 12):
        return False

    blank_lines = len(lines) - len(non_empty)
    if blank_lines < 1:
        return False

    alpha_chars = sum(1 for char in "\n".join(non_empty) if char.isalpha())
    if alpha_chars < 120:
        return False

    return True


def extract_strict_poem_lines(
    raw_text: str,
    title: str,
    author: str,
    *,
    max_non_empty_lines: int = 120,
) -> list[str] | None:
    """Return poem lines when text passes strict full-poem checks."""

    bounded = _slice_between_markers(raw_text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in bounded.split("\n")]
    lines = _trim_front_matter(lines, title, author)
    lines = _trim_tail_sections(lines)

    while lines and _WHITESPACE_LINE_RE.match(lines[0]):
        lines = lines[1:]
    while lines and _WHITESPACE_LINE_RE.match(lines[-1]):
        lines.pop()

    if not lines or not _is_strict_poem_shape(lines, max_non_empty_lines=max_non_empty_lines):
        return None
    return lines


def normalize_gutenberg_candidate(
    candidate: GutenbergCandidate,
    raw_text: str,
    *,
    max_non_empty_lines: int = 120,
) -> NormalizedPoem | NormalizationError:
    """Normalize a strict Gutenberg candidate into canonical poem format."""

    poem_lines = extract_strict_poem_lines(
        raw_text,
        candidate.title,
        candidate.author,
        max_non_empty_lines=max_non_empty_lines,
    )
    if poem_lines is None:
        return NormalizationError(
            reason="strict_extraction_failed",
            input_record={"ebook_id": candidate.ebook_id, "title": candidate.title, "author": candidate.author},
        )

    return normalize_record(
        {
            "title": candidate.title,
            "author": candidate.author,
            "lines": poem_lines,
        }
    )


def ingest_gutenberg_candidates(
    candidates: list[GutenbergCandidate],
    *,
    texts_dir: Path,
    max_non_empty_lines: int = 120,
) -> tuple[list[NormalizedPoem], list[dict]]:
    """Load, strictly parse, and normalize Gutenberg candidates."""

    poems: list[NormalizedPoem] = []
    errors: list[dict] = []

    for candidate in candidates:
        try:
            raw_text = _read_gutenberg_text(texts_dir, candidate.ebook_id)
        except FileNotFoundError as exc:
            errors.append({"kind": "text_missing", "ebook_id": candidate.ebook_id, "reason": str(exc)})
            continue

        normalized = normalize_gutenberg_candidate(
            candidate,
            raw_text,
            max_non_empty_lines=max_non_empty_lines,
        )
        if isinstance(normalized, NormalizationError):
            errors.append(
                {
                    "kind": "extract_error",
                    "ebook_id": candidate.ebook_id,
                    "title": candidate.title,
                    "author": candidate.author,
                    "reason": normalized.reason,
                }
            )
            continue

        poems.append(
            NormalizedPoem(
                title=normalized.title,
                author=normalized.author,
                text=normalized.text,
                linecount=normalized.linecount,
                content_hash=normalized.content_hash,
                source=f"gutenberg:{candidate.ebook_id}",
            )
        )

    return poems, errors
