# DailyPoetry Active Plan

## 2026-02-20 Phase 18: Android "Today's Poem" Home Screen Widget

### Problem Definition
- DailyPoetry can be installed as a PWA on Android, but Android home-screen widgets are not supported by the current web-only stack.
- A Pixel user needs a true widget surface (resizable card on launcher) that shows today's poem without opening the app first.
- The solution must stay aligned with existing backend contracts (`GET /v1/daily`) and avoid introducing duplicate poem-selection logic.

### Proposed Solution
1. Add a small native Android companion app in the monorepo (minimal scope, widget-first).
   - New module, e.g. `daily-poetry-android/`, implemented in Kotlin.
   - Include launcher activity that opens the existing web app URL in Chrome Custom Tab (or default browser intent).
2. Implement an App Widget provider for "Today's Poem".
   - Create widget layouts for compact and expanded sizes.
   - Show poem title, author, and truncated poem body with graceful empty/error states.
   - Tapping widget opens DailyPoetry web app.
3. Fetch data from existing API endpoint.
   - Use `GET /v1/daily` from the widget update worker/provider.
   - Keep date semantics UTC by treating API payload as source of truth.
   - Add caching so widget still renders last known poem when offline.
4. Add periodic refresh scheduling.
   - Update widget on placement, device reboot, and periodic background cadence.
   - Force a refresh near UTC day rollover to keep poem/date current.
5. Add docs and setup scripts.
   - Document local build, signing, install, and widget placement flow.
   - Add configuration for API base URL and production defaults.
6. Add focused Android tests.
   - Unit tests for payload parsing and truncation/format helpers.
   - Instrumented/widget smoke tests where practical.

### Success Criteria
- On a Pixel device, user can add a DailyPoetry widget from launcher widget picker.
- Widget displays current daily poem data from `GET /v1/daily` and opens the app URL when tapped.
- Widget refreshes at least daily without manual intervention and handles offline fallback cleanly.
- Build and setup instructions in repo are sufficient for another developer to run and verify.
- Existing web app and API functionality remain unchanged and passing.

## 2026-02-20 Phase 17: Project Gutenberg Ingestion Adapter

### Problem Definition
- The ingestion pipeline currently depends on PoetryDB as the only corpus source.
- This limits collection diversity and makes corpus growth dependent on a single upstream.
- We need an additional ingestion path that can output artifacts in the same shape consumed by `daily-poetry-api` seeding.

### Proposed Solution
1. Add a source-adapter ingestion path for Project Gutenberg in `daily-poetry-ingest`.
   - Introduce a Gutenberg pipeline that can be selected from CLI (for example, `--source gutenberg`).
   - Keep artifact contracts unchanged: `poems.jsonl`, `duplicates.jsonl`, `authors.jsonl`, `report.json`.
2. Use offline-friendly Gutenberg metadata input.
   - Accept Gutenberg catalog-style metadata file input (CSV) and optional local text directory for poem extraction.
   - Filter for poetry books and public-domain-safe entries.
3. Add deterministic parsing and normalization.
   - Split raw text into poem candidates with explicit, conservative heuristics.
   - Reuse existing normalization + dedupe rules where possible.
   - Preserve poem formatting and compute content hashes for stable IDs.
4. Extend reporting for provenance and quality.
   - Track source-specific metrics: books scanned, poems extracted, poems accepted/rejected, parse errors.
5. Add focused tests.
   - Unit tests for Gutenberg metadata filtering and text extraction heuristics.
   - Integration-style test that verifies generated artifacts are compatible with seed expectations.

### Success Criteria
- Running ingestion with Gutenberg source produces valid JSONL artifacts and report output.
- Artifacts can be seeded by existing `daily-poetry-api/app/seed_from_artifacts.py` without schema changes.
- At least one deterministic test fixture corpus ingests successfully end-to-end.
- Reporting includes Gutenberg-specific extraction counts and error summaries.
- Existing PoetryDB ingestion path remains unchanged and passing.

## 2026-02-20 Phase 15: Post-MVP Product Expansion and Reliability

### Problem Definition
- The app is now functional end-to-end, but product depth and operational reliability are still thin in key areas:
  - limited ingestion source diversity (currently PoetryDB-first),
  - weak author context (bios not meaningfully populated),
  - installability is foundational but not full UX-complete across platforms,
  - no notification loop for daily engagement,
  - no opening visualization/brand moment on app launch,
  - reliability risk if future `daily_selection` scheduling is not continuously maintained.
- Without this phase, growth and retention will be constrained by content variety, context quality, and re-engagement gaps.

### Proposed Solution
1. Content Expansion and Metadata Quality
   - Add a source-adapter pattern in ingestion so additional poem providers can be integrated without rewriting core normalization/dedupe.
   - Track per-poem provenance metadata (`source`, source identifier, optional license field).
   - Extend author enrichment to include short bios and bio source attribution.
   - Seed/store non-empty `authors.bio_short` in API DB and return it in `/v1/daily`.
2. Installability and PWA UX Completion
   - Add frontend install prompt handling (`beforeinstallprompt`) and a user-facing install CTA.
   - Add iOS-specific install guidance fallback when native prompt is unavailable.
   - Validate installability across Android Chrome and iOS Safari behaviors.
3. Engagement Loop: Daily Notifications
   - Implement opt-in notification preference in frontend and backend user profile storage.
   - Add daily reminder delivery path (timezone-aware schedule target).
   - Include an on/off control with clear permission/error states.
4. Visual Product Differentiation
   - Add a lightweight opening visualization for app launch/daily reveal.
   - Keep animation performant and skippable so reading flow remains primary.

### Success Criteria
- Data and content:
  - At least one additional ingestion source is implemented behind an adapter interface and produces compatible artifacts.
  - `authors.bio_short` is populated for a measurable majority of scheduled authors and returned by `/v1/daily`.
  - Ingestion report includes source/provenance summary and author bio coverage metrics.
- Product UX:
  - App presents a clear install CTA where supported and shows iOS fallback guidance where needed.
  - New opening visualization loads without blocking core content and can be skipped.
  - Notification preference can be toggled, persisted, and reflected in UI state reliably.
- Reliability:
  - Automated schedule maintenance keeps at least 30 days of `daily_selection` ahead of current UTC date.
  - Alert path exists for schedule depletion risk.
- Security and quality:
  - Docs contain placeholder-only connection examples.
  - CI runs backend tests and fails on contract regressions in daily/auth/favourites endpoints.

## 2026-02-20 Phase 16: Daily Notifications (Web Push MVP)

### Problem Definition
- DailyPoetry does not currently have a notification loop, so users need to remember to open the app manually each day.
- On free-tier hosting, engagement depends more on proactive reminders because cold starts and low daily habit can reduce return usage.
- The app already has PWA/service worker foundations, but push subscription and delivery plumbing do not yet exist.

### Proposed Solution
1. Backend notification subscription APIs
   - Add authenticated endpoints for users to:
     - save/update a web push subscription,
     - delete a subscription,
     - set notification preference (`enabled`, `time_zone`, `hour_utc` or local-hour preference).
2. Backend storage + migration
   - Add tables for push subscriptions and notification preferences keyed to `users.id`.
   - Keep schema minimal and explicit (no inferred behavior).
3. Push delivery command
   - Add a backend CLI command to send daily reminder notifications to all due+enabled subscribers.
   - Command should be idempotent per UTC day where practical (avoid duplicate sends in one run window).
4. Frontend opt-in flow
   - Add a settings control in app UI:
     - request notification permission,
     - subscribe through service worker push manager,
     - post subscription payload to backend,
     - allow opt-out (unsubscribe + backend delete).
5. Service worker push handler
   - Handle `push` events and display a notification with daily-poem copy.
   - Handle click action to open/focus the app URL.
6. Deployment and operations
   - Add required env vars for VAPID keys and sender contact.
   - Document scheduled job setup (e.g., daily cron hitting CLI/worker command).

### Success Criteria
- Users can enable and disable daily notifications from the app UI.
- Backend stores and removes push subscriptions per authenticated anonymous user.
- Service worker successfully displays notifications when push payloads are sent.
- A scheduled delivery command can run daily and send reminders to eligible subscribers.
- Disabling notifications fully stops future sends for that user subscription.
