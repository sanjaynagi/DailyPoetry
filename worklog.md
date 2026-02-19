# Worklog

## 2026-02-19 11:19:05Z
- Completely renewed `plan.md` with current-state summary and production roadmap.
- Added explicit external service setup guidance for:
  - frontend hosting (Vercel),
  - backend hosting (Render/Fly),
  - managed Postgres (Neon/Supabase/Render Postgres),
  - optional scheduler/cron service.
- Added phased execution plan to reach full functionality, including auth hardening, deployment order, reliability checks, and release readiness gate.
- Added a concrete operator checklist and command reference for ingestion, API run, DB seeding, and app run.

## 2026-02-19 11:15:44Z
- Updated browser tab title from `Daily Poetry` to `DailyPoetry` in `daily-poetry-app/index.html`.
- Rebuilt frontend to refresh generated output and confirm successful build.

## 2026-02-19 11:13:22Z
- Added Phase 7 planning details in `plan.md` for artifact seeding and bottom-tab refinement.
- Implemented API seed/import utility in `daily-poetry-api/app/seed_from_artifacts.py`:
  - loads `authors.jsonl` and `poems.jsonl`.
  - upserts authors (including `image_url`) and poems.
  - generates deterministic `daily_selection` schedule for configurable number of days.
  - supports injected engine/session factory for isolated testing.
- Added seed test in `daily-poetry-api/tests/test_seed.py` and verified seeded author image persistence.
- Updated API docs in `daily-poetry-api/README.md` and workspace docs in `README.md` with seed command.
- Executed seed command against real artifacts:
  - `python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365`
  - seeded summary: 129 authors, 3151 poems, 365 scheduled days.
- Verified scheduled rows with non-null author images exist (e.g., `Alexander Pope` with image URL).
- Updated PWA bottom tab UI:
  - changed tabs to flat split layout with single vertical separator.
  - changed favourites tab label to heart symbol.
  - removed oval button styling from tab controls.
  - files: `daily-poetry-app/src/App.tsx`, `daily-poetry-app/src/styles.css`.
- Verified API tests pass: `pytest -q` in `daily-poetry-api` (2 passed).
- Verified app build passes: `npm run build` in `daily-poetry-app`.

## 2026-02-19 11:07:04Z
- Added Phase 6 planning details in `plan.md` for UI navigation/button polish.
- Updated `daily-poetry-app` UI:
  - moved primary navigation to fixed bottom tab bar in `daily-poetry-app/src/App.tsx`.
  - renamed `Today` tab label to `DailyPoem`.
  - changed date label to date-only with larger typography in `daily-poetry-app/src/components/TodayView.tsx`.
  - replaced text-based favourite action with heart icon button (`♡`/`♥`) in `daily-poetry-app/src/components/TodayView.tsx`.
  - added conditional author image rendering when `image_url` is null.
  - added/updated tab and heart button styling in `daily-poetry-app/src/styles.css`.
- Verified app build passes: `npm run build` in `daily-poetry-app`.

## 2026-02-19 09:58:14Z
- Added Phase 5 backend MVP details to `plan.md` covering API endpoints, schema, and UTC date selection.
- Created new backend service `daily-poetry-api/` using FastAPI + SQLAlchemy.
- Added database schema migration `daily-poetry-api/migrations/001_init.sql` with required tables:
  - `authors`
  - `poems`
  - `daily_selection`
  - `users`
  - `favourites`
- Implemented API modules:
  - `daily-poetry-api/app/main.py`
  - `daily-poetry-api/app/service.py`
  - `daily-poetry-api/app/auth.py`
  - `daily-poetry-api/app/models.py`
  - `daily-poetry-api/app/schemas.py`
  - `daily-poetry-api/app/database.py`
  - `daily-poetry-api/app/migrate.py`
  - `daily-poetry-api/app/init_db.py`
- Implemented endpoints:
  - `GET /v1/daily` (UTC date lookup from `daily_selection`)
  - `GET /v1/me/favourites` (Bearer token user scope)
  - `POST /v1/me/favourites` (Bearer token user scope)
- Added backend tests in `daily-poetry-api/tests/test_api.py` covering endpoint happy path and auth requirement.
- Added backend docs in `daily-poetry-api/README.md` and updated workspace `README.md` to include API project.
- Installed backend dependencies with `python -m pip install -e '.[dev]'`.
- Verified backend tests pass with `pytest -q` (1 passed).

## 2026-02-19 09:48:21Z
- Added Phase 4 planning details in `plan.md` for author image enrichment in ingestion.
- Implemented author image enrichment module in `daily-poetry-ingest/src/daily_poetry_ingest/author_images.py`:
  - Wikipedia API image lookup with retry/backoff.
  - Nullable fallback when no image is found.
- Integrated enrichment stage into `daily-poetry-ingest/src/daily_poetry_ingest/pipeline.py`:
  - Generates `authors.jsonl`.
  - Adds report metrics `authors_enriched` and `authors_without_images`.
  - Appends enrichment errors to `report.json` while keeping ingestion non-fatal.
- Updated package exports in `daily-poetry-ingest/src/daily_poetry_ingest/__init__.py`.
- Added tests in `daily-poetry-ingest/tests/test_author_images.py`.
- Updated ingestion documentation in `daily-poetry-ingest/README.md`.
- Verified ingestion test suite passes: `PYTHONPATH=src python -m unittest discover -s tests` (7 passed).
- Verified CLI entrypoint still works: `PYTHONPATH=src python -m daily_poetry_ingest.cli --help`.

## 2026-02-19 09:39:39Z
- Updated `plan.md` with Phase 3 backend contract integration scope for `/v1/daily` and auth-ready favourites endpoints.
- Wired `daily-poetry-app` favourites to backend-ready API client methods:
  - added `GET /v1/me/favourites` and `POST /v1/me/favourites` in `daily-poetry-app/src/lib/api.ts`.
  - added auth token support via `VITE_AUTH_TOKEN` or local storage key `daily-poetry.auth-token`.
- Refactored favourites state management to include explicit loading/sync/error/source state in `daily-poetry-app/src/hooks/useFavourites.ts`.
- Updated UI to surface loading/error/sync states in:
  - `daily-poetry-app/src/App.tsx`
  - `daily-poetry-app/src/components/FavouritesView.tsx`
  - `daily-poetry-app/src/components/TodayView.tsx`
- Updated type definitions and constants for favourites source/auth key:
  - `daily-poetry-app/src/types/poetry.ts`
  - `daily-poetry-app/src/lib/constants.ts`
- Updated styling for favourites status metadata in `daily-poetry-app/src/styles.css`.
- Updated app documentation for backend/auth usage in `daily-poetry-app/README.md`.
- Verified build success: `npm run build` in `daily-poetry-app`.

## 2026-02-19 09:27:30Z
- Installed `daily-poetry-app` dependencies with elevated permissions (`npm install`).
- Fixed build typing issue by adding `daily-poetry-app/src/vite-env.d.ts` (`/// <reference types="vite/client" />`).
- Verified app build passes: `npm run build` completed successfully.
- Noted npm audit output: 2 moderate vulnerabilities reported by npm in transitive dependencies.

## 2026-02-19 09:26:51Z
- Executed approved phase plan.
- Moved ingestion project into `daily-poetry-ingest/`:
  - moved `pyproject.toml`, `src/`, `tests/`, and ingestion README into the new directory.
  - updated ingestion README commands to write artifacts to `../artifacts/ingestion`.
  - verified ingestion tests pass from new location: `PYTHONPATH=src python -m unittest discover -s tests` (5 passed).
  - verified CLI remains functional: `PYTHONPATH=src python -m daily_poetry_ingest.cli --help`.
- Bootstrapped `daily-poetry-app/` as a Vite-compatible React + TypeScript structure and implemented:
  - `Today` and `Favourites` views.
  - typed daily-poem API client with cached fallback.
  - favourites persistence via local storage.
  - service worker registration and `public/sw.js` with shell caching + network-first `/v1/daily` strategy.
  - base responsive styling and navigation shell.
- Added root workspace `README.md` documenting both projects and run commands.
- Attempted dependency installation for `daily-poetry-app`, but `npm install` hung in sandbox and was terminated.
- Build verification for app currently blocked by missing local dependencies (`tsc: command not found`).

## 2026-02-19 09:18:05Z
- Updated `plan.md` to a combined two-phase plan: extraction of ingestion code into `daily-poetry-ingest/` and initial bootstrap of the `daily-poetry-app/` PWA.
- Defined success criteria and scope boundaries for both phases before implementation.

## 2026-02-18 20:58:25Z
- Confirmed implementation decisions: Python 3.11+, `JSONL + report.json`, and ingest-all-valid policy.
- Added ingestion package scaffold under `src/daily_poetry_ingest` and project config in `pyproject.toml`.
- Implemented multiprocessing ingestion pipeline with queue-based fetch and normalization workers in `src/daily_poetry_ingest/pipeline.py`.
- Implemented canonical normalization and validation in `src/daily_poetry_ingest/normalize.py`.
- Implemented deterministic hash-based deduplication in `src/daily_poetry_ingest/dedupe.py`.
- Added CLI entrypoint in `src/daily_poetry_ingest/cli.py`.
- Added tests for normalization and deduplication invariants in `tests/test_normalize.py` and `tests/test_dedupe.py`.
- Added usage documentation in `README.md`.
- Ran tests successfully with `PYTHONPATH=src python -m unittest discover -s tests` (5 tests passed).

## 2026-02-18 20:52:55Z
- Reviewed repository guidance documents: `agents.md`, `ingestion-design-doc.md`, `daily-poetry-design-doc.md`, and `poetrydb-README.md`.
- Created `plan.md` with problem definition, proposed solution, success criteria, scope, and open decisions for alignment before implementation.
