# Daily Poetry Ingestion Tool

Ingestion pipelines for Daily Poetry (PoetryDB and Project Gutenberg).

## Runtime

- Python 3.11+
- No third-party runtime dependencies

## Install (editable)

```bash
python -m pip install -e .
```

## Run

PoetryDB (default):

```bash
daily-poetry-ingest --source poetrydb --output-dir ../artifacts/ingestion
```

Project Gutenberg (strict extraction):

```bash
daily-poetry-ingest \
  --source gutenberg \
  --gutenberg-catalog-csv /path/to/pg_catalog.csv \
  --gutenberg-texts-dir /path/to/gutenberg-texts \
  --gutenberg-language en \
  --output-dir ../artifacts/ingestion
```

Or without installing the script:

```bash
PYTHONPATH=src python -m daily_poetry_ingest.cli --source poetrydb --output-dir ../artifacts/ingestion
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
- Gutenberg ingestion uses strict heuristics to prioritize full/accurate poem extraction over recall.
