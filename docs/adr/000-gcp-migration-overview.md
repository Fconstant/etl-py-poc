# ADR-000: GCP Migration Overview

**Date:** 2026-07-19
**Status:** Proposed

## Summary

Incremental migration of the ETL pipeline from local filesystem to GCP services, in 3 independent phases.

## ADR Index

| ADR | Decision | Status |
|---|---|---|
| [ADR-001](001-gcp-migration-strategy.md) | 3-phase incremental strategy | Proposed |
| [ADR-002](002-bigquery-data-model.md) | BigQuery: raw + aggregated tables | Proposed |
| [ADR-003](003-keep-polars-transforms.md) | Keep Polars, no SQL transforms | Proposed |
| [ADR-004](004-defer-app-split.md) | Defer core/cli/server split | Proposed |

## Phase Roadmap

```
Phase 1: BigQuery Load (now)
├── ADR-001, ADR-002, ADR-003, ADR-004
├── Add google-cloud-bigquery dependency
├── Add to_bigquery() to load layer
├── Configure GCP credentials (service account)
├── Keep local CSV/Parquet as fallback
└── Output: local files + BigQuery tables

Phase 2: GCS Cache (future)
├── Replace data/cache/ with GCS bucket
├── Polars reads/writes GCS via fsspec
├── TTL via GCS lifecycle rules
└── Pipeline becomes stateless

Phase 3: Cloud Run (future)
├── Dockerfile for the CLI
├── FastAPI server interface (app split)
├── Deploy to Cloud Run
├── HTTP trigger for on-demand runs
└── Cloud Scheduler for daily runs
```

## What We're NOT Doing (intentionally)

- **No Dataflow/Beam** — overkill for ~10K rows
- **No Cloud Composer** — orchestration via Cloud Scheduler is simpler
- **No streaming** — batch pipeline, not real-time
- **No dbt/Dataform** — Polars transforms are sufficient
- **No app split yet** — deferred to Phase 3

## References

- Original POC design: `openspec/changes/archive/2026-07-17-poc-etl-pipeline/design.md`
- Project README: `README.md`
