# Daily Poetry App

Initial PWA foundation for Daily Poetry using React + TypeScript + Vite.

## Setup

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Environment

- `VITE_API_BASE_URL` (optional): backend base URL (default `http://localhost:8000`).
- `VITE_AUTH_TOKEN` (optional): bearer token for `/v1/me/favourites` endpoints.

You can also set a token at runtime in browser local storage under key:
- `daily-poetry.auth-token`

## Implemented v1 Slice

- `Today` view with title, poem body, author card, and favourite toggle.
- `Favourites` view with local persistence.
- Auth-ready favourites integration:
  - `GET /v1/me/favourites`
  - `POST /v1/me/favourites` with `{ poem_id }`
  - Explicit loading/error states with local fallback when auth is missing.
- Offline-first daily poem behavior:
  - API fetch from `/v1/daily`.
  - Fallback to cached daily poem in local storage.
  - Service worker registration and network-first caching for `/v1/daily`.

## Key Files

- `src/lib/api.ts`: typed daily API fetch + fallback.
- `src/hooks/useFavourites.ts`: favourites endpoint sync + fallback logic.
- `public/sw.js`: service worker caching strategy.
- `src/App.tsx`: app shell and routing between Today/Favourites.
