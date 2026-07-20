# Mission: Learn BigQuery & Data Engineering

## Why
Migrating an existing Python ETL pipeline (REST Countries + Universities APIs → Polars → CSV/Parquet) to GCP BigQuery as Phase 1 of a 3-phase cloud migration. Need to understand BigQuery concepts, SQL dialect, Python client, cost model, and data modeling to implement `to_bigquery()` in the load layer and operate confidently on the platform.

## Success looks like
- Can write and optimize GoogleSQL queries against BigQuery tables
- Understands BigQuery pricing (on-demand vs slots) and can avoid surprise bills
- Can load Polars DataFrames into BigQuery tables using `google-cloud-bigquery`
- Understands when to use partitioning/clustering and when to skip it
- Can explain BigQuery architecture (columnar storage, separated compute/storage) to an interviewer

## Constraints
- Traditional fullstack dev background (Node/React/Postgres), new to data engineering and GCP
- Small data scale (~10K rows) — no need for enterprise complexity
- Learning alongside implementation (not separate study period)
- Budget-conscious: want to stay within free tier where possible

## Out of scope
- Cloud Composer / Airflow orchestration (Phase 3)
- BigQuery ML / AI features
- Streaming ingestion
- Dataflow / Apache Beam
- Multi-cloud or hybrid setups
