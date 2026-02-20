# DailyPoetry Plan (Renewed)

## 1. Current Status Summary

### 1.1 What Already Exists

- `daily-poetry-ingest/`
  - PoetryDB ingestion pipeline is working.
  - Outputs:
    - `poems.jsonl`
    - `duplicates.jsonl`
    - `authors.jsonl` (with nullable `image_url`)
    - `report.json`
  - Author image enrichment is implemented (Wikipedia lookup, nullable fallback).

- `daily-poetry-api/`
  - FastAPI backend MVP exists.
  - Endpoints implemented:
    - `GET /v1/daily`
    - `GET /v1/me/favourites`
    - `POST /v1/me/favourites`
  - Schema exists for:
    - `authors`
    - `poems`
    - `daily_selection`
    - `users`
    - `favourites`
  - UTC-based daily selection logic is implemented.
  - Seed utility exists to import ingestion artifacts and schedule daily poems.

- `daily-poetry-app/`
  - PWA frontend exists with:
    - Daily poem screen
    - Favourites screen
    - Bottom tab navigation
    - Heart-style favourite control
    - Offline/cached daily fallback
  - Browser title is now `DailyPoetry`.

### 1.2 What Is Not Yet Fully Production-Ready

- Favourites removal is not yet API-complete (`DELETE` endpoint missing).
- Auth is placeholder token-based (not full anonymous auth lifecycle).
- No production hosting/deployment pipeline configured yet.
- No observability/monitoring/alerting yet.
- No scheduled operational job to guarantee future `daily_selection` coverage.

---

## 2. Target: Fully Functional App

A fully functional DailyPoetry release means:

1. Frontend served publicly (HTTPS) with working API integration.
2. Backend API deployed with persistent Postgres.
3. Daily poem always available for current UTC date.
4. Favourites fully functional (add/list/remove) for anonymous users.
5. Ingestion + seeding operational workflow documented and repeatable.

---

## 3. External Services You Need

## 3.1 Frontend Host (Recommended: Vercel)

- Create Vercel project from this repo.
- Root directory: `daily-poetry-app`.
- Build command: `npm run build`.
- Output directory: `dist`.
- Env var:
  - `VITE_API_BASE_URL=https://<your-api-domain>`

## 3.2 Backend Host (Recommended: Render or Fly.io)

- Create backend service from this repo.
- Root directory: `daily-poetry-api`.
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Env var:
  - `DAILY_POETRY_DATABASE_URL=<postgres-connection-string>`

## 3.3 Managed Postgres (Recommended: Neon, Supabase, or Render Postgres)

- Provision a Postgres instance.
- Set connection string in backend host.
- Run migrations + seed job.

## 3.4 Optional Scheduled Job Service

- Use host-native cron/job feature (Render Cron, Fly Machines cron, GitHub Actions).
- Daily/weekly job to ensure `daily_selection` is pre-populated ahead.

---

## 4. Execution Plan to Production

## Phase A: Complete Backend Contract

### Tasks
- Add `DELETE /v1/me/favourites/{poem_id}`.
- Wire idempotent delete behavior.
- Add tests for delete flow.

### Success Criteria
- App can add/list/remove favourites using API only.

## Phase B: Auth Hardening (Anonymous)

### Tasks
- Implement anonymous identity issuance (or signed token strategy).
- Replace ad-hoc bearer handling with validated token contract.
- Update frontend token storage/bootstrap logic.

### Success Criteria
- New user can open app and favourite without manual token setup.

## Phase C: Data Operations

### Tasks
- Run ingestion when needed (`daily-poetry-ingest`).
- Seed/update backend from artifacts:
  - `python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365`
- Add routine scheduling refresh process.

### Success Criteria
- `/v1/daily` never returns missing-date 404 in normal operation.

## Phase D: Deployments

### Tasks
- Deploy backend + DB first.
- Validate API health and real payloads.
- Deploy frontend with correct API base URL.
- Smoke test full user flow in production URL.

### Success Criteria
- Public URL works end-to-end on mobile and desktop.

## Phase E: Reliability and Safety

### Tasks
- Add structured logs and request IDs.
- Add health/readiness checks.
- Add alerts for:
  - no daily selection for UTC date
  - repeated API 5xx
- Add backup/restore policy for Postgres.

### Success Criteria
- Operational issues are detectable and recoverable.

---

## 5. Immediate Checklist (What You Should Do Next)

1. Choose and provision services:
- Vercel (frontend)
- Render/Fly (backend)
- Neon/Supabase/Render Postgres (database)

2. Deploy backend first:
- Set `DAILY_POETRY_DATABASE_URL`
- Start service
- Confirm `/health` and `/v1/daily`

3. Seed real data:
- Run seed command in backend environment
- Verify `daily_selection` for current UTC date

4. Deploy frontend:
- Set `VITE_API_BASE_URL`
- Verify daily poem renders and heart favourite posts

5. Implement delete-favourite endpoint next (critical remaining feature).

---

## 6. Commands Reference

## Ingestion

```bash
cd daily-poetry-ingest
PYTHONPATH=src python -m daily_poetry_ingest.cli --output-dir ../artifacts/ingestion
```

## API local run

```bash
cd daily-poetry-api
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
```

## Seed API DB from artifacts

```bash
cd daily-poetry-api
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
```

## App local run

```bash
cd daily-poetry-app
npm install
npm run dev
```

---

## 7. Release Readiness Gate

Before public launch, confirm all are true:

- [ ] `GET /v1/daily` stable and UTC-correct.
- [ ] favourites add/list/remove fully API-backed.
- [ ] anonymous auth flow works without manual intervention.
- [ ] 30+ future days scheduled in `daily_selection`.
- [ ] frontend + backend deployed with HTTPS.
- [ ] error monitoring and logs available.

## 8. Phase 8: Anonymous Auth + Full Favourite Sync

### Problem Definition
- Frontend currently requires manual token configuration for backend favourite sync.
- Unfavourite is local-only behavior and not persisted to backend.

### Proposed Solution
1. Backend: add anonymous auth issuance endpoint:
- `POST /v1/auth/anonymous`
- Returns a generated token and user id; creates user if needed.

2. Frontend: token bootstrap on first load:
- If no token in local storage, request anonymous token from backend.
- Store token in `daily-poetry.auth-token`.
- Use it for all favourites requests.

3. Backend: add delete endpoint:
- `DELETE /v1/me/favourites/{poem_id}`
- Idempotent removal semantics.

4. Frontend: wire unfavourite to backend delete:
- Keep optimistic UI behavior.
- Surface sync errors explicitly.

### Success Criteria
- New user can favourite/unfavourite without manually setting token.
- Favourites source is backend (`remote`) by default after bootstrap.
- Refresh preserves favourites via API, not local-only fallback.
- API tests cover anonymous token issuance and delete favourite flow.
