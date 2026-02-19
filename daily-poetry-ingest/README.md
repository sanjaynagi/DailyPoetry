# Daily Poetry Ingestion Tool

PoetryDB ingestion pipeline for Daily Poetry.

## Runtime

- Python 3.11+
- No third-party runtime dependencies

## Install (editable)

```bash
python -m pip install -e .
```

## Run

```bash
daily-poetry-ingest --output-dir ../artifacts/ingestion
```

Or without installing the script:

```bash
PYTHONPATH=src python -m daily_poetry_ingest.cli --output-dir ../artifacts/ingestion
```

## Outputs

The command writes:

- `poems.jsonl`: canonical normalized poems
- `duplicates.jsonl`: records that share `content_hash` with a canonical poem
- `authors.jsonl`: author metadata with nullable `image_url`
- `report.json`: ingestion metrics and error records

## Notes

- Ingestion is safe to rerun and deterministic for canonical output.
- Line and stanza formatting is preserved from PoetryDB `lines` data.
- Multiprocessing with queues is used for fetch and normalization stages.
- Author images are enriched from Wikipedia when available; when unavailable, `image_url` is `null`.
