"""CLI entrypoint for PoetryDB ingestion."""

from __future__ import annotations

import argparse
from pathlib import Path

from daily_poetry_ingest.pipeline import auto_worker_split, print_report, run_ingestion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest poems from PoetryDB into JSONL artifacts")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/ingestion"))
    parser.add_argument("--base-url", default="https://poetrydb.org")
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--backoff-seconds", type=float, default=0.5)
    parser.add_argument("--rate-limit-rps", type=float, default=2.0)
    parser.add_argument("--fetch-workers", type=int, default=None)
    parser.add_argument("--normalize-workers", type=int, default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    fetch_workers = args.fetch_workers
    normalize_workers = args.normalize_workers
    if fetch_workers is None or normalize_workers is None:
        auto_fetch, auto_normalize = auto_worker_split()
        fetch_workers = fetch_workers or auto_fetch
        normalize_workers = normalize_workers or auto_normalize

    report = run_ingestion(
        output_dir=args.output_dir,
        base_url=args.base_url,
        fetch_workers=fetch_workers,
        normalize_workers=normalize_workers,
        timeout_seconds=args.timeout_seconds,
        retries=args.retries,
        backoff_seconds=args.backoff_seconds,
        rate_limit_rps=args.rate_limit_rps,
    )
    print_report(report)


if __name__ == "__main__":
    main()
