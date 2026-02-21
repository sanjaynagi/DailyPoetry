# Daily Poetry API

Backend MVP for Daily Poetry.

## Endpoints

- `POST /v1/auth/anonymous`
- `GET /v1/daily`
- `GET /v1/me/favourites` (Bearer token required)
- `POST /v1/me/favourites` (Bearer token required)
- `DELETE /v1/me/favourites/{poem_id}` (Bearer token required)
- `GET /v1/me/notifications/preferences` (Bearer token required)
- `PUT /v1/me/notifications/preferences` (Bearer token required)
- `POST /v1/me/notifications/subscriptions` (Bearer token required)
- `DELETE /v1/me/notifications/subscriptions` (Bearer token required)

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

Notification env vars:
- `DAILY_POETRY_VAPID_PUBLIC_KEY`
- `DAILY_POETRY_VAPID_PRIVATE_KEY`
- `DAILY_POETRY_VAPID_SUBJECT` (default `mailto:ops@example.com`)

## Seed From Ingestion Artifacts

```bash
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
```

This loads `authors.jsonl` and `poems.jsonl` into DB and schedules daily poems.
Author `image_url` and `bio_short` values from `authors.jsonl` are stored and served via `/v1/daily`.
Schedule generation now uses only poems with `editorial_status='approved'`.

For initial bootstrap where newly inserted poems should be immediately schedulable:

```bash
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365 --new-poem-status approved
```

## UTC Daily Selection

`GET /v1/daily` resolves today's poem using current UTC date against `daily_selection.date`.

## Editorial Moderation CLI

Interactive moderation:

```bash
python -m app.editorial_cli interactive
```

Interactive mode now shows one random poem at a time and prompts:
- `a` approve
- `r` reject
- `s` skip
- `q` quit

Useful commands:

```bash
python -m app.editorial_cli list --status pending --limit 30
python -m app.editorial_cli approve --poem-id <POEM_ID>
python -m app.editorial_cli reject --poem-id <POEM_ID>
python -m app.editorial_cli stats
python -m app.editorial_cli auto-reject-long --max-lines 50 --status pending
```

Send due web push reminders:

```bash
python -m app.notifications_cli --dry-run
python -m app.notifications_cli
```
