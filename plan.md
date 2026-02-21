# DailyPoetry Active Plan

## 2026-02-20 Phase: Author Bio Ingestion and Persistence

### Problem Definition
- The `authors` table already supports `bio_short`, and the API already returns `author.bio_short` in `/v1/daily`.
- Current seed logic does not ingest bios from artifacts and instead writes empty bios on insert.
- Current ingestion author enrichment only resolves image metadata, so future corpus ingestions do not produce structured author bio data.
- Result: the product has author bio display capability but no reliable data pipeline to populate or maintain it.

### Proposed Solution
1. Extend author artifact contract.
- Update `daily-poetry-ingest` author enrichment output so each `authors.jsonl` record includes:
  - `name`
  - `bio_short` (nullable or empty string fallback by policy)
  - `bio_source` (nullable)
  - `bio_url` (nullable)
  - existing image fields (`image_url`, `image_source`)
- Keep artifact generation deterministic and sorted by author name.

2. Add reusable bio enrichment tooling for ingestion.
- Extend the author enrichment module to resolve short biography text from configured sources.
- Add CLI switches to control behavior for future runs:
  - enable/disable bio enrichment
  - source selection
  - max bio length/normalization policy
  - optional overrides file for manual corrections
- Preserve non-fatal behavior: enrichment failures should log errors and continue with null/empty bio fields.

3. Persist bios in API seeding.
- Update `daily-poetry-api/app/seed_from_artifacts.py` so `_upsert_authors` reads and writes `bio_short` from `authors.jsonl`.
- Ensure upsert semantics are explicit:
  - new authors receive artifact-provided bio data,
  - existing authors are updated from artifact rows according to defined precedence.

4. Add editorial override path for long-term quality.
- Introduce an optional checked-in overrides artifact (author keyed) merged after auto-enrichment and before writing `authors.jsonl`.
- This provides stable corrections for ambiguous or low-quality automatic bios.

5. Expand reporting and tests.
- In ingestion report, include bio coverage metrics (authors with bios, without bios, source counts).
- Add/extend tests across ingest and API seed paths to verify:
  - artifact schema includes bio fields,
  - seed persists and updates `bio_short`,
  - API payload continues returning populated `author.bio_short`.

### Success Criteria
- Running ingestion writes `authors.jsonl` with bio fields for all author rows.
- Re-running ingestion is deterministic for author metadata ordering and shape.
- Seeding from artifacts writes non-empty `authors.bio_short` when provided and updates existing rows predictably.
- `/v1/daily` returns populated `author.bio_short` for seeded authors with available bios.
- Tests covering new bio artifact + seed behavior pass in both `daily-poetry-ingest` and `daily-poetry-api`.
