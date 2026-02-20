📘 Design Document 2

Daily Poetry PWA App (v1)

⸻

1. Vision

A calm, beautiful daily ritual.

Open app → Read today’s poem → Optional favourite → Close.

No feeds.
No noise.
No algorithmic churn.

⸻

2. Core Requirements

Functional
	•	Display one global daily poem
	•	Show:
	•	Title
	•	Poem text
	•	Author name
	•	Author image
	•	Short bio
	•	Allow user to favourite poems
	•	View favourites list
	•	Installable PWA
	•	Offline access to today’s poem

⸻

3. Architecture

PWA (React)
    ↓
API (FastAPI / Node)
    ↓
Postgres


⸻

4. Backend API

GET /v1/daily

Returns:

{
  "date": "2026-02-18",
  "poem": {
    "id": "...",
    "title": "...",
    "text": "...",
    "linecount": 14
  },
  "author": {
    "id": "...",
    "name": "...",
    "bio_short": "...",
    "image_url": "..."
  }
}

Server determines “today” using UTC.

⸻

GET /v1/me/favourites

Authenticated endpoint.

⸻

POST /v1/me/favourites

Body:

{ "poem_id": "uuid" }


⸻

5. Daily Selection Model

Table: daily_selection

date (date, unique)
poem_id (fk)

Admin pre-populates future dates.

Optional:
	•	Pre-generate 365 days in advance.

⸻

6. Authentication Strategy

Use anonymous auth (e.g., Supabase or JWT-based).

Flow:
	•	On first visit:
	•	Generate anonymous user ID
	•	Store token in local storage
	•	Favourites tied to user ID

Upgradeable later to email login.

⸻

7. PWA Architecture

Tech Stack
	•	React + Vite
	•	TypeScript
	•	Service Worker
	•	IndexedDB (for offline caching)

Caching Strategy

Cache:
	•	/v1/daily
	•	Favourited poems

Offline behavior:
	•	If offline, show last cached daily poem
	•	Show offline banner

⸻

8. UX Structure

Screen 1 — Today

[Title]
[Poem body]

— Author Name

[Author image]
[Short bio]

[♡ Favourite]

Minimal UI.
High typography quality.

⸻

Screen 2 — Favourites

List:
	•	Title
	•	Author
	•	Date featured

Click → opens poem detail

⸻

9. Typography Considerations (Important)

Poetry UX depends heavily on:
	•	Line spacing
	•	Indentation
	•	Serif font
	•	Dark/light mode

We should:
	•	Preserve exact line breaks
	•	Avoid reflow errors
	•	Disable justification
	•	Support dynamic font scaling

⸻

10. Performance

Daily endpoint should:
	•	Be cached at CDN edge
	•	Be <50KB payload

Target:
	•	<200ms TTFB

⸻

11. Push Notifications (Phase 2)

Daily at 9am local time:

“Today’s poem is ready.”

Requires:
	•	Service Worker push subscription
	•	Backend cron job

⸻

12. Analytics (Minimal)

Track:
	•	Daily opens
	•	Favourites per poem
	•	Retention

Avoid invasive tracking.

⸻

13. Deployment Strategy

Backend
	•	Fly.io / Render / Railway
	•	Postgres managed

Frontend
	•	Vercel

⸻

14. Future Features
	•	Theme-based months
	•	Author spotlight weeks
	•	Share as image
	•	Reading streak counter
	•	Multi-language support

⸻

Strategic Summary

Ingestion Tool
→ Own your data
→ Curate carefully
→ Avoid runtime dependency

PWA App
→ Calm, simple
→ Server-owned daily selection
→ Offline-first
→ Anonymous auth