"""Deterministic deduplication helpers for normalized poems."""

from __future__ import annotations

from dataclasses import asdict

from daily_poetry_ingest.normalize import NormalizedPoem


def dedupe_poems(poems: list[NormalizedPoem]) -> tuple[list[dict], list[dict]]:
    """Split normalized poems into canonical and duplicate records.

    Determinism rule: canonical winner for a hash is the lexicographically
    smallest tuple (author, title, text).
    """

    grouped: dict[str, list[NormalizedPoem]] = {}
    for poem in poems:
        grouped.setdefault(poem.content_hash, []).append(poem)

    canonical: list[dict] = []
    duplicates: list[dict] = []

    for content_hash in sorted(grouped.keys()):
        group = grouped[content_hash]
        ordered = sorted(group, key=lambda p: (p.author, p.title, p.text))
        winner = ordered[0]
        canonical.append(asdict(winner))
        for duplicate in ordered[1:]:
            record = asdict(duplicate)
            record["canonical_content_hash"] = winner.content_hash
            duplicates.append(record)

    canonical.sort(key=lambda p: (p["author"], p["title"], p["content_hash"]))
    duplicates.sort(
        key=lambda p: (p["author"], p["title"], p["content_hash"], p["canonical_content_hash"])
    )
    return canonical, duplicates
