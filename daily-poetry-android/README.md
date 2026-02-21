# daily-poetry Android Widget

Native Android companion app that exposes a Pixel-compatible home-screen widget for daily-poetry.

## What it does

- Adds a `Today's Poem` launcher widget via `AppWidgetProvider`.
- Fetches poem data from `GET /v1/daily`.
- Caches the most recent payload locally for offline fallback.
- Refreshes on:
  - widget add/update,
  - manual refresh button tap,
  - periodic background work (6h cadence),
  - reboot/date/time/timezone changes.
- Opens the web app URL when the widget card is tapped.

## Configuration

Set production defaults in `app/build.gradle.kts`:

- `DAILY_POETRY_API_BASE_URL`
- `DAILY_POETRY_WEB_APP_URL`

For a local API, change `DAILY_POETRY_API_BASE_URL` to your machine-accessible endpoint.

## Build and run

1. Open `daily-poetry-android/` in Android Studio (Jellyfish+).
2. Let Android Studio sync Gradle.
3. Run the `app` target on a Pixel device/emulator (API 26+).
4. Long press home screen -> `Widgets` -> `daily-poetry Widget` -> `Today's Poem`.

## Verify behavior

1. Widget shows title/author/date/body from `/v1/daily`.
2. Tap widget body opens daily-poetry web app.
3. Tap refresh icon forces immediate update.
4. Disable network and confirm last cached poem remains visible.

## Notes

- This module is intentionally widget-first and minimal.
- Publishing to Play Store requires app signing, release build, privacy policy, and store listing assets.
