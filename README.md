# Daily Poetry Workspace

This repository now contains three projects:

- `daily-poetry-ingest/`: Python 3.11+ ingestion pipeline for PoetryDB.
- `daily-poetry-app/`: React + TypeScript PWA app scaffold.
- `daily-poetry-api/`: FastAPI backend MVP with daily and favourites endpoints.

## Ingestion

```bash
cd daily-poetry-ingest
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m daily_poetry_ingest.cli --output-dir ../artifacts/ingestion
```

## PWA App

```bash
cd daily-poetry-app
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to your backend origin when available.

## API

```bash
cd daily-poetry-api
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
```
