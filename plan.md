# DailyPoetry Plan (Live System)

## 1. Current State (As Of 2026-02-20)

DailyPoetry is now live and functioning end-to-end.

### 1.1 Live Components
- Frontend (`daily-poetry-app`) deployed on Vercel.
- Backend (`daily-poetry-api`) deployed on Render.
- Database on Supabase Postgres.
- Ingestion pipeline (`daily-poetry-ingest`) producing and enriching poem/author artifacts.

### 1.2 Confirmed Working Flows
- `GET /v1/daily` is serving real current data.
- Anonymous auth issuance is implemented (`POST /v1/auth/anonymous`).
- Favourites are backend-backed:
  - `GET /v1/me/favourites`
  - `POST /v1/me/favourites`
  - `DELETE /v1/me/favourites/{poem_id}`
- Favourites persist across refresh.
- Favourites UI can display the poem text.

### 1.3 Recent Stability Fixes
- CORS configured for Vercel -> Render browser requests.
- Supabase/Render connectivity resolved using proper connection settings.
- `daily_selection.date` converted to real `DATE` in Supabase.

---

## 2. Primary Goal (Next Stage)

Move from “working live app” to “operationally robust product” with safe content operations, predictable scheduling, and better production observability.

---

## 3. Next Milestones

## Milestone A: Production Hardening (Immediate)

### Problem
The app works, but runtime and operational safeguards are minimal.

### Tasks
1. Remove temporary DB type-compatibility workarounds now that `daily_selection.date` is `DATE`.
2. Add structured API error logging.
3. Add API-level request logging for key endpoints.
4. Add explicit health/readiness checks for DB connectivity.

### Success Criteria
- API behaves cleanly with strict date typing.
- Failures are observable from logs without manual reproduction.

## Milestone B: Data Operations Reliability

### Problem
Daily schedule continuity depends on manual seeding behavior.

### Tasks
1. Add automated schedule maintenance job (Render cron or GitHub Actions).
2. Guarantee at least N future days scheduled (e.g., 365).
3. Add alert/notification path when future scheduled days drop below threshold (e.g., 30).

### Success Criteria
- `/v1/daily` does not fail due to schedule exhaustion.
- Team receives early warning before schedule gaps.

## Milestone C: Editorial Safety

### Problem
All ingested poems are schedulable without an editorial state gate.

### Tasks
1. Add `editorial_status` to poems (`pending`, `approved`, `rejected`).
2. Update schedule generation to use only `approved` poems.
3. Add simple admin script to review/approve poems.

### Success Criteria
- Daily poem selection only uses curated content.
- Content quality issues can be controlled without code changes.

## Milestone D: UX and Product Iteration

### Problem
Core UX works but still has room for refinement and trust cues.

### Tasks
1. Improve favourite sync feedback (e.g., “Synced” / “Retrying”).
2. Add dedicated favourite poem detail view (instead of only expandable inline details).
3. Add empty/error states with clearer user messaging.
4. Continue typography/layout polish for mobile reading comfort.

### Success Criteria
- User sees reliable feedback for sync state.
- Favourite poem reading flow feels intentional and clean.

## Milestone E: Monitoring and Release Discipline

### Problem
No formal operational dashboard/alerts/release checklist in place.

### Tasks
1. Add production monitoring tool and alerting rules.
2. Add deployment checklist (API first, then frontend).
3. Add smoke test script for post-deploy verification:
- `/health`
- `/v1/daily`
- anonymous token issuance
- favourite add/remove

### Success Criteria
- Regressions are detected quickly.
- Releases are repeatable and lower-risk.

---

## 4. What You Should Do Next (Operator Checklist)

1. Redeploy latest backend and frontend commits.
2. Confirm CORS env is exact (no trailing slash origins).
3. Run smoke checks in production:
- `/health`
- `/v1/daily`
- favourite add/remove from browser.
4. Set up schedule-maintenance cron.
5. Prioritize editorial_status implementation.

---

## 5. Command Reference

## Ingestion
```bash
cd daily-poetry-ingest
PYTHONPATH=src python -m daily_poetry_ingest.cli --output-dir ../artifacts/ingestion
```

## API local
```bash
cd daily-poetry-api
python -m pip install -e '.[dev]'
pytest -q
uvicorn app.main:app --reload
```

## Seed from artifacts
```bash
cd daily-poetry-api
python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365
```

## App local
```bash
cd daily-poetry-app
npm install
npm run build
npm run dev
```

---

## 6. Definition of “Healthy Production”

- Daily poem endpoint stable and UTC-correct.
- Favourites fully remote-synced for anonymous users.
- 365 future daily selections maintained.
- Editorial gate controls publishable poems.
- Monitoring and alerts active for API and schedule health.


## 9. Phase 9: Dark Mode UI

### Problem Definition
- UI currently ships with a single light theme and no user-controlled theme preference.

### Proposed Solution
1. Add light/dark color tokens using CSS variables.
2. Add theme toggle control in app shell.
3. Persist user preference in localStorage.
4. Default to system preference when no explicit user setting exists.

### Success Criteria
- User can switch between light and dark mode.
- Theme choice persists across reloads.
- Dark mode is legible and visually coherent across primary screens.
