# ADR-003: Keep Polars Transforms — No SQL Duplication

**Date:** 2026-07-19
**Status:** Proposed
**Deciders:** diplo
**Related:** ADR-001 (Phase 1), ADR-002 (data model)

## Context

With BigQuery as output, there's a temptation to move transforms into SQL (BigQuery views, materialized views). This ADR decides whether to keep Polars transforms or migrate to SQL.

## Decision

**Keep Polars transforms in Python.** BigQuery is output-only; it stores results but doesn't execute transforms.

### Transform flow (unchanged)

```
Extract (httpx) → Transform (Polars) → Load (BigQuery + local files)
```

### What stays in Polars
- Country name normalization (difflib fuzzy matching)
- University-country join
- Enrichment (select + rename columns)
- Aggregation (group_by, count, sort, head)

### What goes to BigQuery
- Table storage (raw + aggregated)
- Ad-hoc SQL queries (manual, via console)
- Future dashboarding (Looker Studio, etc.)

## Rationale

**Why not SQL transforms:**
- Polars transforms are already working and tested
- Fuzzy matching (`difflib.get_close_matches`) has no SQL equivalent
- Python transforms are easier to debug and version
- Avoids maintaining two transform layers (Polars + SQL)

**Why not BigQuery Scheduled Queries:**
- Adds complexity without value at this scale
- Polars is faster for <100K rows
- BigQuery costs per query (even if minimal)

**When SQL transforms would make sense:**
- Data volume exceeds Polars memory capacity
- Team prefers SQL over Python
- Need real-time transforms on streaming data
- Regulatory requirement for SQL auditability

## Consequences

- Transforms remain pure Python functions
- BigQuery tables are written, not queried (in pipeline flow)
- Ad-hoc analysis possible via BigQuery console (manual SQL)
- No need to learn BigQuery SQL dialect for transforms
- Future: if data grows, can add BigQuery views as read-through cache

## References

- Polars docs: group_by, join, select
- BigQuery: external tables, scheduled queries (not used here)
