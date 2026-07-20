# ADR-001: GCP Migration Strategy — Incremental Phases

**Date:** 2026-07-19
**Status:** Proposed
**Deciders:** diplo

## Context

The ETL pipeline is a working POC with local filesystem for cache and output. The goal is to evolve it into a cloud-native pipeline using GCP services, motivated by:
- Portfolio/interview signal for GCP-focused companies
- Practical learning of GCP data engineering services
- Incremental migration (not a rewrite)

## Decision

Adopt a 3-phase incremental migration:

### Phase 1: BigQuery Load (current)
- Add `to_bigquery()` alongside existing `to_csv()` / `to_parquet()`
- Pipeline writes to both local files AND BigQuery
- No app restructuring; CLI stays as-is
- GCP credentials via service account (ADC)

### Phase 2: GCS Cache (future)
- Replace `data/cache/` with Google Cloud Storage bucket
- Polars reads/writes GCS via `fsspec` / `gcsfs`
- TTL via GCS lifecycle rules (replaces file-mtime check)
- Pipeline becomes stateless (no local disk dependency)

### Phase 3: Cloud Run Deployment (future)
- Dockerfile for the CLI
- Optional FastAPI server interface for HTTP triggers
- Deploy to Cloud Run (scale to zero)
- Cloud Scheduler for daily/weekly runs

## Rationale

**Why phases instead of all-at-once:**
- Each phase is independently valuable
- Reduces cognitive load and blast radius
- Avoids "big bang" rewrites that stall
- Each phase can be verified before moving to next

**Why BigQuery first:**
- Lowest complexity (only changes load layer)
- Highest portfolio signal (data warehouse is core data engineering)
- No app restructuring required
- Polars ↔ BigQuery integration is mature (`google-cloud-bigquery` + PyArrow)

**Why not Dataflow/Beam:**
- Overkill for this data volume (~10K rows)
- Adds Apache Beam dependency and complexity
- Better suited for streaming or 100K+ row datasets

**Why not Cloud Composer first:**
- Orchestration is Phase 3 concern
- Requires running infrastructure (cost + ops)
- Cloud Scheduler + Cloud Run is simpler for cron-like scheduling

## Consequences

- Each phase has its own ADR (ADR-002, ADR-003, ADR-004)
- App split (core/cli/server) deferred to Phase 3
- BigQuery data model decided in ADR-002
- GCP project setup (billing, APIs, credentials) needed before Phase 1

## References

- OpenSpec change: `poc-etl-pipeline` (original POC design)
- GCP docs: BigQuery Python client, Cloud Storage, Cloud Run
