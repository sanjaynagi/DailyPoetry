# Project Gutenberg Data Setup

This doc shows how to download the Project Gutenberg offline catalog and text files, prepare them for the DailyPoetry strict ingester, and run ingestion.

## 1. Download Catalog (`pg_catalog.csv`)

```bash
mkdir -p data/gutenberg
cd data/gutenberg
curl -L -o pg_catalog.csv https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv
```

## 2. Download Text Corpus Bundle

```bash
curl -L -o txt-files.tar.zip https://www.gutenberg.org/cache/epub/feeds/txt-files.tar.zip
unzip txt-files.tar.zip
tar -xf txt-files.tar
```

## 3. Build a Flat Text Directory for Ingestion

The ingester expects files discoverable as `<id>.txt` (it also supports `pg<id>.txt` and `<id>-0.txt`).

```bash
mkdir -p gutenberg-texts
find . -type f \( -name '*-0.txt' -o -name 'pg*.txt' -o -name '[0-9]*.txt' \) | \
while IFS= read -r f; do
  b="$(basename "$f")"
  if [[ "$b" =~ ^pg?([0-9]+)(-0)?\.txt$ ]]; then
    cp -n "$f" "gutenberg-texts/${BASH_REMATCH[1]}.txt"
  fi
done
```

## 4. Run Gutenberg Ingestion

From repo root:

```bash
cd daily-poetry-ingest
PYTHONPATH=src python -m daily_poetry_ingest.cli \
  --source gutenberg \
  --gutenberg-catalog-csv ../data/gutenberg/pg_catalog.csv \
  --gutenberg-texts-dir ../data/gutenberg/gutenberg-texts \
  --gutenberg-language en \
  --output-dir ../artifacts/ingestion
```

## Notes

- `txt-files.tar.zip` is large, so download on a stable connection with enough disk space.
- The Gutenberg pipeline in this repo uses strict extraction heuristics to prioritize full/accurate poems over recall.
- Prefer official offline feeds/catalogs over scraping site pages.

## References

- https://www.gutenberg.org/ebooks/offline_catalogs.html
- https://www.gutenberg.org/cache/epub/feeds/
- https://www.gutenberg.org/policy/robot_access.html
