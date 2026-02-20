# DailyPoetry

DailyPoetry is a full-stack app that serves one poem per UTC day, supports anonymous users, and persists favourites to a backend database.

This monorepo contains:
- `daily-poetry-ingest/`: PoetryDB + Project Gutenberg ingestion pipelines with author enrichment (Python 3.11+).
- `daily-poetry-api/`: FastAPI backend (`/v1/daily`, auth issuance, favourites APIs).
- `daily-poetry-app/`: Vite + React + TypeScript PWA frontend.
- `daily-poetry-android/`: Native Android widget companion app (Kotlin, AppWidgetProvider).
- `artifacts/ingestion/`: generated JSONL/report artifacts used for DB seeding.

## Current Architecture

- Data sources: PoetryDB and Project Gutenberg via ingestion pipeline.
- Artifacts: `poems.jsonl`, `authors.jsonl`, `duplicates.jsonl`, `report.json`.
- Database schema: `authors`, `poems`, `daily_selection`, `users`, `favourites`.
- Daily selection: resolved from `daily_selection.date` using UTC date.
- Auth model: anonymous token issuance (`POST /v1/auth/anonymous`) used for favourites.

## Repository Setup

Prerequisites:
- Python 3.11+
- Node.js 18+
- npm

### 1. Run ingestion

```bash
cd daily-poetry-ingest
python -m pip install -e .
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m daily_poetry_ingest.cli --output-dir ../artifacts/ingestion
```

### 2. Run API locally

```bash
cd daily-poetry-api
python -m pip install -e '.[dev]'
python -m app.init_db
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
uvicorn app.main:app --reload
```

Environment:
- `DAILY_POETRY_DATABASE_URL` (optional; defaults to local SQLite DB).
- `DAILY_POETRY_CORS_ORIGINS` (comma-separated origins for browser clients).

### 3. Run app locally

```bash
cd daily-poetry-app
npm install
npm run dev
```

Environment:
- `VITE_API_BASE_URL` (optional, defaults to `http://localhost:8000`).

## API Surface (MVP)

- `POST /v1/auth/anonymous`
- `GET /v1/daily`
- `GET /v1/me/favourites` (Bearer token)
- `POST /v1/me/favourites` (Bearer token)
- `DELETE /v1/me/favourites/{poem_id}` (Bearer token)
- `GET /v1/me/notifications/preferences` (Bearer token)
- `PUT /v1/me/notifications/preferences` (Bearer token)
- `POST /v1/me/notifications/subscriptions` (Bearer token)
- `DELETE /v1/me/notifications/subscriptions` (Bearer token)

## Production Deployment

Recommended stack currently used:
- Frontend: Vercel
- Backend: Render
- Database: Supabase Postgres

Deployment/setup steps are documented in `instructions.md`.

## Useful Commands

Ingestion:
```bash
cd daily-poetry-ingest
PYTHONPATH=src python -m daily_poetry_ingest.cli --source poetrydb --output-dir ../artifacts/ingestion
```

Gutenberg ingestion (strict extraction):
```bash
cd daily-poetry-ingest
PYTHONPATH=src python -m daily_poetry_ingest.cli --source gutenberg --gutenberg-catalog-csv /path/to/pg_catalog.csv --gutenberg-texts-dir /path/to/gutenberg-texts --output-dir ../artifacts/ingestion
```

Seed database from artifacts:
```bash
cd daily-poetry-api
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
```

Editorial moderation CLI:
```bash
cd daily-poetry-api
python -m app.editorial_cli interactive
```

API tests:
```bash
cd daily-poetry-api
pytest -q
```

Frontend build:
```bash
cd daily-poetry-app
npm run build
```

Android widget app (open in Android Studio):
```bash
cd daily-poetry-android
```

## Pre-commit Hooks

Install and enable repository hooks:

```bash
python -m pip install pre-commit
pre-commit install
```

Run all hooks manually:

```bash
pre-commit run --all-files
```
