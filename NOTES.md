# Design Notes & Results

Running log of design decisions and measured results. Source material for the README and interview talking points.

## Decisions

### Single Postgres + pgvector database (2026-10-17)
- **Choice:** one Postgres 16 instance with the pgvector extension (Docker image `pgvector/pgvector:pg16`, pgvector 0.8.7).
- **Why:** vectors, full-text search (`tsvector`) and the structured XBRL financial tables live in one DB. Hybrid search can then be a single SQL query, metadata filters (ticker, year, form, section) are plain `WHERE` clauses, and there is only one service to deploy.
- **Alternatives considered:** a dedicated vector DB (Pinecone, Qdrant, Weaviate). It would scale better for ANN search, but adds a second system to keep in sync, and full-text plus SQL joins would need extra glue.

### edgartools for filing download + section parsing (2026-10-17)
- **Choice:** `edgartools` (v5.62) fetches filings from EDGAR and splits 10-Ks into Items (`tenk["Item 1A"]`).
- **Why:** writing a robust 10-K section parser (inconsistent HTML, the table of contents repeating Item headings) is a project of its own. edgartools handles it, and the item boundaries were clean on the first three filings (see below).
- **Risk to watch:** parse quality may vary across companies and older filings. Check every new ticker for empty or truncated sections.

## Results

### Item 1A extraction sanity check (2026-10-17)
| Ticker | Period of report | Filed | Item 1A chars |
|---|---|---|---|
| AAPL | 2025-09-27 | 2025-10-31 | 68,163 |
| MSFT | 2026-06-30 | 2026-07-29 | 81,066 |
| NVDA | 2026-01-25 | 2026-02-25 | 114,773 |

All three start at the real "Risk Factors" text (not the table of contents) and end before Item 1B.
Note: fiscal year comes from the period-of-report year. NVDA's fiscal year ends in late January, so "FY2026" covers mostly calendar 2025. This matters when comparing companies by year.
