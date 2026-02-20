# DailyPoetry Deployment Instructions (Vercel + Render + Supabase)

This guide gives a practical path to run DailyPoetry in production using:
- Supabase for Postgres
- Render for the backend API
- Vercel for the frontend PWA

## 0. Prerequisites

1. Accounts
- Supabase account
- Render account
- Vercel account
- GitHub repo already pushed

2. Local tooling
- `python` 3.11+
- `node` + `npm`
- `gh` optional (for GitHub tasks)

3. Repository structure
- `daily-poetry-ingest/` (ingestion)
- `daily-poetry-api/` (backend)
- `daily-poetry-app/` (frontend)

---

## 1. Supabase: Create Postgres Database

1. Create a new Supabase project.
2. In Supabase Dashboard, copy the Postgres connection string from:
- `Project Settings` -> `Database` -> `Connection string`
3. Use an SSL-enabled SQLAlchemy URL, for example:

```text
postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres?sslmode=require
```

Note: SQLAlchemy in this project expects a SQLAlchemy-compatible URL. Use `postgresql+psycopg://...`.

---

## 2. Render: Deploy Backend API (`daily-poetry-api`)

## 2.1 Create Render Web Service

1. In Render, click `New` -> `Web Service`.
2. Connect your GitHub repo.
3. Configure:
- Name: `dailypoetry-api` (or your preferred name)
- Root Directory: `daily-poetry-api`
- Runtime: `Python`
- Build Command:

```bash
pip install -e '.[dev]'
```

- Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 2.2 Configure environment variables in Render

Set:

- `DAILY_POETRY_DATABASE_URL=postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres?sslmode=require`

## 2.3 Deploy and verify API

Once deployed, verify:

```bash
curl https://<your-render-api-domain>/health
```

Expected:

```json
{"status":"ok"}
```

---

## 3. Seed Data Into Supabase

The backend has a seed utility that imports ingestion artifacts (`authors.jsonl`, `poems.jsonl`) and creates future `daily_selection` rows.

Run from your machine (recommended):

```bash
cd daily-poetry-api
export DAILY_POETRY_DATABASE_URL='postgresql+psycopg://postgres.wqvsywfzoixmxyqgbpnm:PW@aws-1-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require'
python -m pip install -e '.[dev]'
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
```

Then verify:

```bash
curl https://<your-render-api-domain>/v1/daily
```

If no schedule exists for current UTC date, this endpoint returns 404. Re-run seeding with enough `--schedule-days`.

---

## 4. Vercel: Deploy Frontend (`daily-poetry-app`)

1. In Vercel, import your GitHub repo.
2. Set project root to:
- `daily-poetry-app`
3. Build settings:
- Build command: `npm run build`
- Output directory: `dist`

## 4.1 Set environment variables in Vercel

Required:
- `VITE_API_BASE_URL=https://<your-render-api-domain>`

Optional (current auth placeholder):
- `VITE_AUTH_TOKEN=<some-stable-token-for-testing>`

Deploy.

---

## 5. End-to-End Validation

After both deployments:

1. Open Vercel URL.
2. Confirm daily poem loads.
3. Favourite a poem.
4. Reload and confirm favourite persists.
5. Confirm API endpoints directly:

```bash
curl https://<your-render-api-domain>/v1/daily
curl -H "Authorization: Bearer <TOKEN>" https://<your-render-api-domain>/v1/me/favourites
```

---

## 6. Recommended Next Production Steps

1. Implement `DELETE /v1/me/favourites/{poem_id}` and wire frontend unfavourite to backend.
2. Replace placeholder bearer token with true anonymous auth issuance.
3. Add a scheduled job to keep `daily_selection` always pre-populated.
4. Add monitoring/alerts for API errors and missing daily selection.
5. Add custom domains for API and app.

---

## 7. Common Issues

1. `GET /v1/daily` returns 404
- Cause: no `daily_selection` row for current UTC date.
- Fix: run seed command with sufficient `--schedule-days`.

2. DB connection errors on Render
- Cause: bad connection string or SSL mode.
- Fix: verify env var and include `sslmode=require`.

3. Frontend still calling localhost API
- Cause: missing or wrong `VITE_API_BASE_URL` in Vercel.
- Fix: update env var and redeploy.
