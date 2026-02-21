# Worklog

## 2026-02-21 00:05:02Z
- Updated favourites poem item styling in `daily-poetry-app/src/styles.css`:
  - removed outline/border from `.favourite-row`,
  - adjusted row background shading to remain visually distinct from surrounding background without using an outline.
- Verified frontend build passes: `cd daily-poetry-app && npm run build`.

## 2026-02-21 00:00:33Z
- Executed next-step runtime operations for author bio rollout.
- Regenerated ingestion artifacts with bios:
  - command: `cd daily-poetry-ingest && PYTHONPATH=src python -m daily_poetry_ingest.cli --source poetrydb --output-dir ../artifacts/ingestion`
  - result:
    - `authors_requested: 129`
    - `authors_enriched: 129`
    - `authors_with_bios: 128`
    - `authors_without_bios: 1`
    - `canonical_poems: 3151`
- Reseeded API database from refreshed artifacts:
  - command: `cd daily-poetry-api && python -m app.seed_from_artifacts --artifacts-dir ../artifacts/ingestion --schedule-days 365`
  - summary:
    - `authors: 129`
    - `poems: 3151`
    - `approved_poems: 1`
    - `scheduled_days: 2`
    - `start_date: 2026-02-21`
- Verified seeded bio presence in DB:
  - command query showed `authors_total=135`, `authors_with_nonempty_bio=134`.

## 2026-02-20 23:56:28Z
- Implemented author bio ingestion and persistence across ingestion + API seeding.
- Ingestion (`daily-poetry-ingest`):
  - Extended author enrichment in `src/daily_poetry_ingest/author_images.py` to include nullable bio metadata fields:
    - `bio_short`
    - `bio_source`
    - `bio_url`
  - Added bio normalization/truncation logic and Wikipedia page URL derivation.
  - Added ingestion controls in `src/daily_poetry_ingest/cli.py`:
    - `--enrich-author-bios` / `--no-enrich-author-bios`
    - `--author-bio-max-chars`
  - Wired new options through `src/daily_poetry_ingest/pipeline.py` for both PoetryDB and Gutenberg paths.
  - Added report metrics:
    - `authors_with_bios`
    - `authors_without_bios`
- API seed (`daily-poetry-api`):
  - Updated `app/seed_from_artifacts.py` `_upsert_authors` to read/write `bio_short` from `authors.jsonl`.
  - Existing authors now get `bio_short` updates during reseed.
- Tests:
  - Updated ingestion tests in `daily-poetry-ingest/tests/test_author_images.py` for bio fields.
  - Extended API seed tests in `daily-poetry-api/tests/test_seed.py`:
    - verifies `bio_short` insert behavior,
    - verifies reseed updates existing author bios.
  - Verified passing:
    - `cd daily-poetry-ingest && PYTHONPATH=src python -m unittest discover -s tests` (11 passed)
    - `cd daily-poetry-api && pytest -q` (6 passed)
- Documentation:
  - Updated `daily-poetry-ingest/README.md`, `daily-poetry-api/README.md`, and root `README.md` for bio fields and CLI controls.

## 2026-02-20 23:48:57Z
- Fixed Postgres startup migration failure during notification flag type coercion.
- Updated `daily-poetry-api/app/migrate.py` schema repair logic to:
  - drop legacy integer defaults before altering flag columns to boolean,
  - convert existing values with explicit `USING` clause,
  - restore boolean defaults after conversion (`push_subscriptions.active=TRUE`, `notification_preferences.enabled=FALSE`).
- Verified backend tests pass: `cd daily-poetry-api && pytest -q` (5 passed).

## 2026-02-20 23:44:14Z
- Reset `plan.md` and replaced prior multi-phase content with a focused phase plan for author bio ingestion and persistence.
- New plan includes:
  - clear problem definition for missing bio population despite existing DB/API support,
  - ingestion artifact contract updates for bio fields,
  - reusable enrichment tooling for future ingestions,
  - API seed upsert changes for `bio_short`,
  - optional editorial override workflow and expanded test/report criteria.

## 2026-02-20 23:36:41Z
- Fixed production notifications subscription 500 caused by Postgres type mismatch (`integer` vs `boolean`).
- Updated migration runner in `daily-poetry-api/app/migrate.py`:
  - added Postgres startup schema repair for legacy notification flag columns:
    - `push_subscriptions.active`
    - `notification_preferences.enabled`
  - when these columns are integer-like, they are coerced to boolean via explicit `USING` conversion.
- Verified backend tests pass: `cd daily-poetry-api && pytest -q` (5 passed).

## 2026-02-20 23:30:23Z
- Refined theme slider geometry to center the thumb precisely over each icon in both light/dark states.
- Updated `daily-poetry-app/src/styles.css`:
  - switched theme track to a two-column grid for exact icon centering,
  - introduced size/padding CSS variables for consistent toggle math,
  - updated thumb translation formula to align center-to-center with each icon.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 23:29:11Z
- Replaced top-right theme toggle icon button with a dual-icon slider control.
- Updated `daily-poetry-app/src/App.tsx`:
  - theme toggle now renders both sun/moon icons with a moving thumb track.
- Updated `daily-poetry-app/src/styles.css`:
  - added polished switch container, track, icon, and thumb styles,
  - added dark-mode thumb position animation via `.theme-toggle-dark`.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 23:27:50Z
- Investigated reminders toggle failure showing browser-level `Failed to fetch`.
- Updated frontend notification error handling in `daily-poetry-app/src/hooks/useNotifications.ts`:
  - map generic fetch failures to an actionable API connectivity/configuration message including current API base URL.
- Updated `daily-poetry-app/src/lib/constants.ts`:
  - production fallback API URL now defaults to `https://dailypoetry-api.onrender.com` when `VITE_API_BASE_URL` is not set.
  - local development behavior remains `http://localhost:8000`.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 23:26:05Z
- Adjusted poem heart action background in `daily-poetry-app/src/styles.css` to avoid split visual artifacts.
- Reintroduced a soft rounded background using a light blend of existing panel/card colors:
  - `background: color-mix(in srgb, var(--poem-card-bg) 64%, var(--panel-bg) 36%)`
  - retained enlarged icon and cleaner styling.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 23:24:28Z
- Enhanced poem favourite action icon styling in `daily-poetry-app/src/styles.css`.
- Updated heart action to a cleaner icon-only treatment:
  - removed circular button chrome (background, border, shadow),
  - slightly increased icon size,
  - refined hover color/scale behavior while preserving active fill state.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 23:22:47Z
- Refined notifications UX in favourites tab for a cleaner premium layout.
- Updated `daily-poetry-app/src/components/FavouritesView.tsx`:
  - changed label text to `Daily reminder`,
  - replaced On/Off button copy with a switch-style slider control,
  - positioned reminder panel above a distinct favourites content box.
- Updated `daily-poetry-app/src/styles.css`:
  - added polished slider visuals and active thumb motion,
  - introduced `.favourites-box` styling,
  - improved reminder panel surface treatment and focus states.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 23:17:39Z
- Moved daily reminders notification controls from the poem tab to the favourites tab.
- Updated component wiring:
  - removed notifications props/UI from `daily-poetry-app/src/components/TodayView.tsx`
  - added notifications panel/props in `daily-poetry-app/src/components/FavouritesView.tsx`
  - rewired notification props in `daily-poetry-app/src/App.tsx`
- Verified frontend build passes: `npm run build`.

## 2026-02-20 22:42:30Z
- Implemented native Android widget companion module in `daily-poetry-android` for Pixel-compatible home-screen placement.
- Added Android project scaffolding and widget runtime:
  - `daily-poetry-android/app/src/main/java/com/dailypoetry/widget/TodayPoemWidgetProvider.kt`
  - `daily-poetry-android/app/src/main/java/com/dailypoetry/widget/WidgetUpdateWorker.kt`
  - `daily-poetry-android/app/src/main/java/com/dailypoetry/widget/WidgetUpdateScheduler.kt`
  - `daily-poetry-android/app/src/main/java/com/dailypoetry/widget/DailyPoemRepository.kt`
  - `daily-poetry-android/app/src/main/java/com/dailypoetry/widget/TodayPoemWidgetRenderer.kt`
- Wired app widget metadata/layout/resources and manifest receivers:
  - `daily-poetry-android/app/src/main/res/xml/today_poem_widget_info.xml`
  - `daily-poetry-android/app/src/main/res/layout/widget_today_poem.xml`
  - `daily-poetry-android/app/src/main/AndroidManifest.xml`
- Added offline cache fallback for daily payloads and manual refresh interaction.
- Added formatter unit tests in `daily-poetry-android/app/src/test/java/com/dailypoetry/widget/PoemFormattersTest.kt`.
- Documented setup and verification in `daily-poetry-android/README.md`.
- Updated root docs to include Android module in `README.md`.

## 2026-02-20 22:37:50Z
- Added Phase 18 planning section in `plan.md`: Android "Today's Poem" home-screen widget.
- Captured concrete problem definition, implementation approach, and measurable success criteria for a Pixel-compatible Android widget backed by existing `/v1/daily` API data.
- Paused before implementation to align on plan/scope per project instruction.

## 2026-02-20 22:17:49Z
- Implemented Project Gutenberg ingestion adapter with strict poem extraction in `daily-poetry-ingest`.
- Added new module `daily-poetry-ingest/src/daily_poetry_ingest/gutenberg.py`:
  - parses Gutenberg catalog CSV entries,
  - applies strict metadata filtering for poetry/single-poem candidates,
  - strips Project Gutenberg boilerplate markers,
  - performs strict poem-shape validation for full/accurate extraction,
  - normalizes candidates into canonical ingestion records.
- Extended ingestion pipeline in `daily-poetry-ingest/src/daily_poetry_ingest/pipeline.py`:
  - added `run_poetrydb_ingestion` (explicit PoetryDB path),
  - added `run_gutenberg_ingestion` (strict Gutenberg path),
  - kept `run_ingestion` as a backward-compatible alias to PoetryDB,
  - unified artifact/report writing across sources.
- Updated CLI in `daily-poetry-ingest/src/daily_poetry_ingest/cli.py`:
  - new `--source` selector (`poetrydb` or `gutenberg`),
  - Gutenberg flags: `--gutenberg-catalog-csv`, `--gutenberg-texts-dir`, `--gutenberg-language`.
- Updated package exports in `daily-poetry-ingest/src/daily_poetry_ingest/__init__.py`.
- Added Gutenberg tests:
  - `daily-poetry-ingest/tests/test_gutenberg.py` for strict filtering/extraction behavior.
  - `daily-poetry-ingest/tests/test_pipeline_gutenberg.py` for end-to-end artifact/report generation.
- Updated docs:
  - `daily-poetry-ingest/README.md` with PoetryDB and Gutenberg usage.
  - `README.md` with multi-source ingestion command examples.
- Validation:
  - `PYTHONPATH=src python -m unittest discover -s tests` (ingest) passed: 11 tests.

## 2026-02-20 21:53:44Z
- Implemented Phase 16 Web Push notification MVP across backend and frontend.
- Backend (`daily-poetry-api`):
  - Added notification schemas and endpoints in `app/main.py`:
    - `GET /v1/me/notifications/preferences`
    - `PUT /v1/me/notifications/preferences`
    - `POST /v1/me/notifications/subscriptions`
    - `DELETE /v1/me/notifications/subscriptions`
  - Added notification data models in `app/models.py`:
    - `NotificationPreference`
    - `PushSubscription`
  - Added migration `migrations/003_notifications.sql` for notification tables/indexes.
  - Added notification preference/subscription service logic in `app/service.py`.
  - Added VAPID config getters in `app/config.py`.
  - Added push send engine in `app/notifications.py`.
  - Added send CLI in `app/notifications_cli.py`.
  - Added `pywebpush` dependency in `pyproject.toml`.
- Frontend (`daily-poetry-app`):
  - Added notification API methods in `src/lib/api.ts`.
  - Added `VITE_VAPID_PUBLIC_KEY` constant in `src/lib/constants.ts`.
  - Added notification preference type in `src/types/poetry.ts`.
  - Added notification opt-in/out hook in `src/hooks/useNotifications.ts`.
  - Wired notification state/actions into `src/App.tsx` and `src/components/TodayView.tsx`.
  - Added notification toggle UI styles in `src/styles.css`.
  - Added push and notification-click handlers in `public/sw.js`.
- Documentation updates:
  - `README.md` API surface expanded with notifications endpoints.
  - `daily-poetry-api/README.md` updated with notification env vars/endpoints/CLI command.
  - `daily-poetry-app/README.md` updated with `VITE_VAPID_PUBLIC_KEY` and notification behavior.
- Test/validation:
  - Added backend notification delivery test in `daily-poetry-api/tests/test_notifications.py`.
  - Expanded API endpoint tests in `daily-poetry-api/tests/test_api.py` for notifications flows.
  - Verified backend tests pass: `pytest -q` (5 passed).
  - Verified frontend build passes: `npm run build`.

## 2026-02-20 21:36:55Z
- Added repository-wide pre-commit configuration in `.pre-commit-config.yaml`.
- Enabled low-friction baseline hooks:
  - Python AST validation for API/ingest Python files,
  - JSON/TOML/YAML structure checks,
  - merge conflict, trailing whitespace, EOF newline, mixed line ending checks,
  - private key and large added file detection.
- Documented setup and usage in `README.md`:
  - `python -m pip install pre-commit`
  - `pre-commit install`
  - `pre-commit run --all-files`

## 2026-02-20 21:26:37Z
- Removed visible author info container chrome in `daily-poetry-app/src/styles.css`.
- Updated `.author-panel` styling to be transparent with no radius/shadow/padding so author details sit without a boxed card.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 21:23:25Z
- Improved daily poem loading UX in `daily-poetry-app` to handle Render free-tier cold starts more clearly.
- Updated `daily-poetry-app/src/App.tsx`:
  - replaced static loading-only splash with a structured loading shell,
  - added explicit loading copy ("Loading today's poem" + server wake-up message),
  - added spinner and indeterminate progress bar elements.
- Updated `daily-poetry-app/src/styles.css`:
  - added loading shell layout and loading typography styles,
  - added animated spinner (`loading-spin`) and moving progress fill (`loading-progress`).
- Verified frontend build passes: `npm run build`.

## 2026-02-20 21:18:37Z
- Added Phase 15 planning section in `plan.md`: `Post-MVP Product Expansion and Reliability`.
- Captured concrete problem definition, proposed solution tracks, and measurable success criteria for:
  - ingestion source expansion and provenance,
  - author bio enrichment and API surfacing,
  - installability UX completion,
  - daily notifications,
  - opening visualization,
  - scheduling reliability guardrails,
  - security/release hygiene.

## 2026-02-20 20:44:56Z
- Moved theme toggle to a global top-right screen position for consistent access across views.
- Updated `daily-poetry-app/src/App.tsx`:
  - added fixed-position app-shell theme toggle button.
  - removed per-view theme-toggle prop wiring into `TodayView`.
- Updated `daily-poetry-app/src/components/TodayView.tsx`:
  - removed inline theme toggle from daily panel header.
  - kept date display in panel header area.
- Updated `daily-poetry-app/src/styles.css`:
  - added `.app-theme-toggle` with safe-area-aware top/right positioning.
  - removed now-unused `.panel-header` layout block.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 20:41:26Z
- Implemented Android installability foundations for the frontend PWA in `daily-poetry-app`.
- Added web app manifest: `daily-poetry-app/public/manifest.webmanifest`.
- Added required install icons generated from existing 1024x1024 logo:
  - `daily-poetry-app/public/icon-192.png`
  - `daily-poetry-app/public/icon-512.png`
  - `daily-poetry-app/public/icon-192-maskable.png`
  - `daily-poetry-app/public/icon-512-maskable.png`
- Linked manifest in `daily-poetry-app/index.html`.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 20:23:35Z
- Added GitHub Actions workflow for backend tests only: `.github/workflows/api-pytests.yml`.
- Workflow runs on `push` and `pull_request` for API-related paths:
  - `daily-poetry-api/**`
  - `.github/workflows/api-pytests.yml`
- CI job configuration:
  - Python 3.11
  - installs backend with dev extras: `python -m pip install -e ".[dev]"`
  - runs backend tests: `pytest -q`
- This intentionally excludes ingest-only changes from triggering API CI.

## 2026-02-20 20:20:21Z
- Investigated Pixel 8a bottom viewport underfill issue in frontend shell.
- Added dynamic viewport height handling in `daily-poetry-app/src/styles.css`:
  - introduced `--viewport-height` token with `100vh` fallback and `100dvh` when supported,
  - applied viewport token to `body`, `.page`, `.content-wrap`, and `.loading-splash`,
  - added root height chain for `html` and `#root`.
- Verified frontend build passes: `npm run build`.

## 2026-02-20 20:06:24Z
- Fixed persistent Supabase pooler `DuplicatePreparedStatement` failures in interactive moderation by updating DB engine connect args in `daily-poetry-api/app/database.py`.
- Added psycopg-specific connection option for Postgres URLs:
  - `prepare_threshold=None` for `postgresql+psycopg` connections.
- This disables server-side prepared statements, which avoids pooler conflicts in both read and write query paths.
- Verified backend tests pass after change: `pytest -q` (4 passed).

## 2026-02-20 20:02:17Z
- Fixed Supabase pooler compatibility issue in bulk moderation path (`DuplicatePreparedStatement`) by changing `auto_reject_long_poems` to a single set-based SQL `UPDATE` in `daily-poetry-api/app/editorial_cli.py`.
- Removed ORM row-by-row flush for this command; now uses one transactional update statement and returns affected row count.
- Verified backend tests pass: `pytest -q` (4 passed).
- Verified command execution still works locally:
  - `python -m app.editorial_cli auto-reject-long --max-lines 30 --status pending`

## 2026-02-20 19:52:31Z
- Added bulk editorial rule command to reject long poems automatically in `daily-poetry-api/app/editorial_cli.py`:
  - new command: `auto-reject-long`
  - default threshold: `--max-lines 50`
  - default scope: `--status pending` (safe default; does not overwrite reviewed poems).
- Added test coverage for long-poem auto rejection in `daily-poetry-api/tests/test_editorial_cli.py`.
- Updated command reference in `daily-poetry-api/README.md`.
- Verified backend tests pass: `pytest -q` (4 passed).
- Executed bulk moderation action on local DB:
  - `python -m app.editorial_cli auto-reject-long --max-lines 50 --status pending`
  - result: rejected 812 poems.

## 2026-02-20 19:49:06Z
- Refactored editorial interactive CLI to random single-poem moderation flow in `daily-poetry-api/app/editorial_cli.py`.
- Interactive mode now shows one random poem at a time (full text) and prompts:
  - approve (`a`)
  - reject (`r`)
  - skip (`s`)
  - quit (`q`)
- Kept non-interactive moderation commands (`list`, `approve`, `reject`, `stats`) unchanged.
- Added test coverage for random picker behavior in `daily-poetry-api/tests/test_editorial_cli.py`.
- Updated operator docs in `daily-poetry-api/README.md`.
- Verified:
  - `pytest -q` (4 passed)
  - `python -m app.editorial_cli interactive` (manual smoke with `q`).

## 2026-02-20 19:44:50Z
- Fixed SQLite migration edge case causing `editorial_status` index creation to fail before column availability on existing local DBs.
- Updated migration normalization in `daily-poetry-api/app/migrate.py`:
  - robust regex conversion of `ADD COLUMN IF NOT EXISTS` for SQLite,
  - fallback self-healing path that adds `editorial_status` and retries index creation when needed.
- Verified moderation CLI works against local SQLite DB:
  - `python -m app.editorial_cli stats`
  - `python -m app.editorial_cli interactive`

## 2026-02-20 19:41:53Z
- Added Phase 11 planning section for editorial moderation workflow in `plan.md`.
- Implemented editorial gating foundations in backend:
  - Added `editorial_status` to `poems` in `daily-poetry-api/migrations/001_init.sql` and `daily-poetry-api/app/models.py`.
  - Added migration `daily-poetry-api/migrations/002_editorial_status.sql` for existing databases.
  - Upgraded migration runner in `daily-poetry-api/app/migrate.py` to apply all SQL migrations in order.
- Updated seed/scheduling workflow in `daily-poetry-api/app/seed_from_artifacts.py`:
  - new poems receive configurable status (`--new-poem-status`),
  - schedule generation now uses only approved poems,
  - explicit error when scheduling is requested but no approved poems exist (unless `--allow-empty-approved-schedule`).
- Added interactive editorial moderation CLI in `daily-poetry-api/app/editorial_cli.py`:
  - `interactive`, `list`, `approve`, `reject`, `stats` commands,
  - interactive approve/reject/view and filtering/search controls.
- Updated docs:
  - `daily-poetry-api/README.md`
  - root `README.md`
- Added/updated tests:
  - new `daily-poetry-api/tests/test_editorial_cli.py`,
  - expanded `daily-poetry-api/tests/test_seed.py` for approved-only scheduling behavior.
- Verified backend tests pass: `pytest -q` (4 passed).

## 2026-02-20 19:10:09Z
- Updated root repository documentation in `README.md` to reflect current system behavior and deployment reality.
- Replaced outdated scaffold text with:
  - current monorepo structure,
  - architecture summary (ingest -> artifacts -> API -> app),
  - local setup flow for ingestion, API, and app,
  - current API endpoint contract,
  - production hosting stack (Vercel + Render + Supabase),
  - operational command reference.
- Intentionally excluded UI enhancement history from `README.md` per request.

## 2026-02-20 19:04:26Z
- Removed the vertical separator from bottom navigation by updating tab layout structure and CSS grid in `daily-poetry-app/src/App.tsx` and `daily-poetry-app/src/styles.css`.
- Added typed DailyPoetry logo to the top of the favourites page, matching the poem page treatment and theme-aware asset switching in `daily-poetry-app/src/components/FavouritesView.tsx`.
- Passed current theme into favourites view from `daily-poetry-app/src/App.tsx`.
- Verified frontend build passes (`npm run build`).

## 2026-02-20 19:00:26Z
- Added Phase 10 (Premium UI Polish) in `plan.md` with explicit problem statement, solution approach, and success criteria.
- Implemented premium polish pass in `daily-poetry-app`:
  - Added richer visual atmosphere and accent tokens in `daily-poetry-app/src/styles.css`.
  - Refined spacing, typography, and surface hierarchy for poem and author sections in `daily-poetry-app/src/styles.css`.
  - Improved interaction polish for toggle, heart action, and tab controls (hover/focus/active behavior).
  - Upgraded bottom navigation chrome for a cleaner, more modern tab bar.
  - Added subtle entrance animation and smoother UI transitions.
- Added UTC-safe date presentation utility in `daily-poetry-app/src/lib/date.ts`.
- Updated displayed dates:
  - Daily view now uses long formatted date in `daily-poetry-app/src/components/TodayView.tsx`.
  - Favourites metadata now uses short formatted date in `daily-poetry-app/src/components/FavouritesView.tsx`.
- Verified frontend build passes (`npm run build`).

## 2026-02-20 18:57:36Z
- Completed a full visual “sleek pass” in `daily-poetry-app/src/styles.css` focused on modern polish while preserving existing IA and behavior.
- Updated design tokens for both themes (light + dark) with more cohesive color relationships and improved contrast tuning.
- Refined panel, card, and row surfaces to use softer translucency, reduced visual noise, and cleaner depth cues.
- Tightened typography and spacing rhythm across the shell and content areas for a calmer, more premium reading experience.
- Modernized navigation chrome and tab treatment with improved separators, emphasis states, and balanced visual weight.
- Smoothed interaction feel with short transition timing on core UI properties for theme switches and state changes.
- Verified frontend build passes after changes (`npm run build`).

## 2026-02-20 18:40:23Z
- Added DailyPoetry tab logo switching by theme in `daily-poetry-app/src/App.tsx`:
  - light theme uses `/dailypoetry-dark.png`
  - dark theme uses `/dailypoetry-light.png`
- Added logo sizing style in `daily-poetry-app/src/styles.css`.
- Copied logo assets into app static directory:
  - `daily-poetry-app/public/dailypoetry-light.png`
  - `daily-poetry-app/public/dailypoetry-dark.png`
- Verified frontend build passes (`npm run build`).

## 2026-02-20 18:24:28Z
- Created feature branch `feature/dark-mode-ui` for isolated UI experimentation.
- Added Phase 9 dark mode plan section to `plan.md` with problem definition, solution, and success criteria.
- Implemented frontend dark mode in `daily-poetry-app`:
  - Added persisted theme state and system-default fallback in `daily-poetry-app/src/App.tsx`.
  - Added theme storage key in `daily-poetry-app/src/lib/constants.ts`.
  - Added CSS token system and dark theme overrides in `daily-poetry-app/src/styles.css`.
  - Added top-right theme toggle control in app shell.
- Verified frontend build passes (`npm run build`).

## 2026-02-20 18:21:18Z
- Fully renewed `plan.md` to reflect current live/functional production state.
- Replaced legacy “build-to-first-deploy” plan sections with a post-launch roadmap focused on:
  - production hardening,
  - scheduling/data operations reliability,
  - editorial safety controls,
  - UX iteration,
  - monitoring and release discipline.
- Added a current operator checklist and updated command reference aligned to the live architecture (Vercel + Render + Supabase).

## 2026-02-20 18:14:48Z
- Added Phase 8 planning details in `plan.md` for anonymous auth issuance, frontend token bootstrap, backend-backed unfavourite, and favourites poem viewing.
- Backend API changes:
  - Added `POST /v1/auth/anonymous` in `daily-poetry-api/app/main.py`.
  - Added `DELETE /v1/me/favourites/{poem_id}` in `daily-poetry-api/app/main.py`.
  - Implemented anonymous token issuance and delete-favourite service logic in `daily-poetry-api/app/service.py`.
  - Extended favourites payload to include poem text (`poem_text`) in `daily-poetry-api/app/service.py` and `daily-poetry-api/app/schemas.py`.
- Frontend changes:
  - Implemented automatic anonymous token bootstrap in `daily-poetry-app/src/lib/api.ts` via `POST /v1/auth/anonymous`.
  - Added backend delete-favourite integration in `daily-poetry-app/src/lib/api.ts`.
  - Updated favourite sync flow in `daily-poetry-app/src/hooks/useFavourites.ts` to use remote add/remove operations.
  - Added expandable poem viewing in favourites UI in `daily-poetry-app/src/components/FavouritesView.tsx`.
  - Added styles for expandable favourites poem content in `daily-poetry-app/src/styles.css`.
- Updated API and app documentation:
  - `daily-poetry-api/README.md`
  - `daily-poetry-app/README.md`
- Verified backend tests pass (`pytest -q`, 2 passed) and frontend build passes (`npm run build`).

## 2026-02-19 18:48:49Z
- Updated `instructions.md` to use Render instead of Fly.io for backend deployment.
- Replaced Fly-specific setup, env, and verification steps with Render Web Service instructions.
- Removed plaintext credential-like connection string and replaced with safe placeholder examples only.

## 2026-02-19 18:42:27Z
- Added `instructions.md` with step-by-step deployment/setup guidance for Supabase (Postgres), Fly.io (API), and Vercel (frontend).
- Included required environment variables, deployment order, seed/import command, verification commands, and common troubleshooting paths.

## 2026-02-19 12:32:15Z
- Added root `.gitignore` covering OS/editor files, Python caches/build artifacts, Node modules/build artifacts, local DB files, env files, and runtime artifacts.
- Linked local repository to GitHub remote `sanjaynagi/DailyPoetry`.
- Resolved nested repository conflict by moving `daily-poetry-app/.git` aside so the workspace can be tracked as a single repo.
- Created initial repository commit: `3cddd40` (`Initial DailyPoetry workspace setup`).
- Pushed `main` to `origin` (`git@github.com:sanjaynagi/DailyPoetry.git`).

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
