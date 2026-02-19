Excellent. I’ll write these as proper high-level engineering design documents — clear scope, architecture, data model, risks, and iteration plan.

⸻

📘 Design Document 1

Poetry Ingestion Tool (v1 — PoetryDB-based)

⸻

1. Purpose

Build a one-time + repeatable ingestion pipeline that:
	•	Pulls poems from PoetryDB
	•	Normalizes and cleans formatting
	•	Enriches metadata
	•	Stores everything in our own database
	•	Removes runtime dependency on PoetryDB

This tool is not part of the production request path.
It is an internal data acquisition + curation system.

⸻

2. Goals

Functional
	•	Import full corpus from PoetryDB
	•	De-duplicate poems
	•	Normalize author names
	•	Preserve stanza formatting exactly
	•	Attach canonical author records
	•	Allow re-runs safely (idempotent)

Non-Goals
	•	No end-user UI
	•	No direct exposure to app users
	•	No real-time PoetryDB proxying

⸻

3. System Overview

High-Level Flow

PoetryDB API
    ↓
Ingestion Script (ETL)
    ↓
Normalization + Cleaning
    ↓
Metadata Enrichment (Wikipedia/Wikidata)
    ↓
Postgres Database


⸻

4. Architecture

Components

1️⃣ Fetcher
	•	Pull list of authors from /author
	•	For each author:
	•	Fetch all poems
	•	Respect rate limits
	•	Retry with exponential backoff

2️⃣ Normalizer
Transforms PoetryDB JSON into internal schema.

Key transformations:
	•	Join lines array into canonical text with \n
	•	Preserve stanza breaks
	•	Normalize whitespace
	•	Strip trailing blank lines
	•	Standardize quotation marks (optional)

3️⃣ De-duplication Engine
PoetryDB sometimes contains:
	•	Duplicate titles
	•	Variant titles
	•	Duplicate poems across formatting

Strategy:
	•	Compute content hash of poem text
	•	Unique index on hash
	•	Log collisions

4️⃣ Metadata Enricher
For each author:
	•	Query Wikipedia API
	•	Extract:
	•	Short description
	•	Birth/death years
	•	Image URL
	•	Store Wikidata ID for future refresh

Caching required.

5️⃣ Validator
Reject poems if:
	•	N lines (e.g., 200 — avoid epics initially)
	•	Missing author
	•	Missing text
	•	Suspicious formatting

⸻

5. Database Schema (Ingestion Side)

authors

id (uuid)
name (text, unique)
birth_year (int, nullable)
death_year (int, nullable)
wikipedia_url (text)
wikidata_id (text)
bio_short (text)
image_url (text)
created_at
updated_at

poems

id (uuid)
title (text)
author_id (fk)
text (text)
linecount (int)
content_hash (text, unique)
source (text)  // e.g., "poetrydb"
license (text) // "public domain"
created_at
updated_at

Indexes:
	•	unique(content_hash)
	•	index(author_id)
	•	index(linecount)

⸻

6. Ingestion Strategy

Phase 1 — Bulk Snapshot
	1.	Fetch /author
	2.	For each author:
	•	Fetch all poems
	3.	Store raw JSON locally
	4.	Run normalization pass
	5.	Insert into DB

Phase 2 — Cleanup Pass
	•	Remove poems > 120 lines (initial filter)
	•	Remove malformed entries
	•	Manual review sampling

⸻

7. Idempotency & Re-runs

Key principle:

Ingestion must be safe to run multiple times.

Mechanisms:
	•	Unique constraint on content_hash
	•	Upsert authors on name
	•	Log changes rather than overwrite silently

⸻

8. Operational Considerations

Rate Limiting

Throttle requests to:
	•	1–5 req/sec
	•	Configurable

Logging

Log:
	•	Fetch failures
	•	Parse errors
	•	Duplicate collisions
	•	Wikipedia misses

⸻

9. Editorial Layer (Critical)

We should not auto-publish everything.

After ingestion:

Create an editorial_status column in poems:
	•	pending_review
	•	approved
	•	rejected

Only approved poems can be selected for daily use.

This prevents:
	•	Overly long poems
	•	Weak content
	•	Formatting errors

⸻

10. Output of Ingestion Tool

After v1 ingestion:
	•	~1000–3000 poems (estimate)
	•	Clean, normalized, curated dataset
	•	Fully independent of PoetryDB

⸻

11. Risks

Risk	Mitigation
PoetryDB changes	Snapshot early
Copyright uncertainty	Restrict to clearly public-domain authors
Poor formatting	Manual review layer
English-only bias	Add other sources later


⸻

12. Future Extensions
	•	Add Wikisource ingestion
	•	Add Gutenberg bulk parser
	•	Add tagging classifier (theme detection via NLP)
	•	Add reading-time estimation
