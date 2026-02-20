# Daily Poetry API

Backend MVP for Daily Poetry.

## Endpoints

- `POST /v1/auth/anonymous`
- `GET /v1/daily`
- `GET /v1/me/favourites` (Bearer token required)
- `POST /v1/me/favourites` (Bearer token required)
- `DELETE /v1/me/favourites/{poem_id}` (Bearer token required)

## Database

Set `DAILY_POETRY_DATABASE_URL` (defaults to `sqlite:///./daily_poetry.db`).

Schema migration file:
- `migrations/001_init.sql`

Run migrations manually:

```bash
python -m app.init_db
```

Migrations also run on app startup.

## Run

```bash
uvicorn app.main:app --reload
```

## Seed From Ingestion Artifacts

```bash
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
```

This loads `authors.jsonl` and `poems.jsonl` into DB and schedules daily poems.
Author `image_url` values from `authors.jsonl` are stored and served via `/v1/daily`.

## UTC Daily Selection

`GET /v1/daily` resolves today's poem using current UTC date against `daily_selection.date`.
