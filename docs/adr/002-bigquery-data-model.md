# ADR-002: BigQuery Data Model — Raw + Aggregated Tables

**Date:** 2026-07-19
**Status:** Proposed
**Deciders:** diplo
**Related:** ADR-001 (Phase 1)

## Context

Phase 1 of GCP migration adds BigQuery as an output destination. The pipeline currently produces:
- Enriched data (university_name, country, iso_code, continent, population, currency_name)
- Aggregated tables (per_country, per_continent, top10)

Need to decide: what goes into BigQuery, and how?

## Options Considered

### Option A: Aggregated tables only
Load only the three output tables (~200, ~6, ~10 rows).

Pros: Simple, matches current output exactly.
Cons: Loses raw data. Can't re-aggregate or slice differently in SQL.

### Option B: Raw enriched + aggregated tables (chosen)
Load enriched data as a fact table, plus the three aggregated tables.

Pros: Raw data preserved for ad-hoc SQL queries. Aggregated tables pre-computed for fast reads.
Cons: Slightly more setup. Duplicated aggregation (Polars + stored results).

### Option C: Raw only, aggregate in SQL
Load only enriched data. Create views for aggregations.

Pros: Single source of truth. Aggregation in SQL.
Cons: Duplicates transform logic. SQL overhead on read.

## Decision

**Option B.** Load raw enriched data + aggregated tables as separate BigQuery tables.

### Schema

```sql
-- Raw enriched data (fact table)
CREATE TABLE etl_universities.universities (
    university_name STRING,
    country STRING,
    iso_code STRING,
    continent STRING,
    population INT64,
    currency_name STRING
);

-- Aggregated outputs
CREATE TABLE etl_universities.universities_per_country (
    country STRING,
    university_count INT64
);

CREATE TABLE etl_universities.universities_per_continent (
    continent STRING,
    university_count INT64
);

CREATE TABLE etl_universities.top10_universities (
    country STRING,
    university_count INT64
);
```

### Design choices

- **No partitioning:** Data volume (~10K rows raw, ~200 aggregated) doesn't justify partitioning overhead.
- **No clustering:** At this scale, full scan is faster than clustering metadata.
- **Write disposition:** `WRITE_TRUNCATE` (overwrite on each run). This is a batch pipeline, not streaming.
- **Dataset:** `etl_universities` (single dataset for all tables).

## Rationale

- Raw data preserved enables ad-hoc analysis in BigQuery console
- Aggregated tables are pre-computed for dashboards/reports
- Polars transforms stay in Python (no SQL duplication)
- Simple schema, no partitioning/clustering complexity

## Consequences

- BigQuery client needs project ID + dataset ID configuration
- Credentials via GCP service account (ADC flow)
- `google-cloud-bigquery` + `pyarrow` dependencies added
- Local CSV/Parquet output retained as fallback
- Pipeline writes to both local files AND BigQuery

## References

- BigQuery Python client: `google-cloud-bigquery`
- Polars ↔ Arrow integration: `df.write_arrow()` / `pl.from_arrow()`
- GCP ADC: https://cloud.google.com/docs/authentication/application-default-credentials
