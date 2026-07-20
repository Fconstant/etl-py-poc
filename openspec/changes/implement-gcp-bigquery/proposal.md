## Why

The ETL pipeline currently outputs only to local files (CSV/Parquet). Adding Google BigQuery as an output destination advances the project toward GCP cloud-native architecture (per ADR-001 Phase 1), provides portfolio signal for data engineering roles, and enables ad-hoc SQL analysis in BigQuery console. Phase 1 is the lowest-complexity entry point — only the load layer changes, with no app restructuring.

## What Changes

- **Add `google-cloud-bigquery` dependency** to `pyproject.toml`
- **Add `to_bigquery()` function** in `src/load/` — writes DataFrames to BigQuery tables with `WRITE_TRUNCATE` disposition. Shared by both `etl run --export-bigquery` (best-effort, via pipeline) and `etl export-bq` (hard-fail, from disk).
- **`etl run` is local-only by default**: writes all 4 DataFrames to local CSV/Parquet only. No network, no GCP dependency. BigQuery upload requires explicit `--export-bigquery` / `--export-bq` flag.
- **Save enriched DataFrame locally** as `data/output/universities.csv` and `data/output/universities.parquet` — previously enriched was only in-memory; now persisted alongside aggregated outputs (8 files total)
- **New `etl export-bq` CLI command**: reads the 4 Parquet files from `data/output/` and uploads them to BigQuery. Does NOT re-run the pipeline. Fails with clear error if output files are missing or BigQuery write fails.
- **Add GCP configuration** — project ID, dataset ID, credentials via Application Default Credentials (ADC) — through environment variables or a config module
- **Create BigQuery dataset and tables** on first write if they don't exist (idempotent setup)

## Capabilities

### New Capabilities

- `bigquery-load`: Write enriched and aggregated Polars DataFrames to BigQuery tables (`etl_universities.universities`, `etl_universities.universities_per_country`, `etl_universities.universities_per_continent`, `etl_universities.top10_universities`) using `WRITE_TRUNCATE` disposition. Authenticate via GCP Application Default Credentials. Handle missing dataset/table with automatic creation. Used by both `etl run --export-bigquery` and `etl export-bq`.
- `bigquery-config`: Configure GCP project ID, dataset ID, and credentials location via environment variables (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_BIGQUERY_DATASET`) or a configuration module. Validate configuration at startup before attempting BigQuery operations.

### Modified Capabilities

- `etl-aggregate-load`: The load phase now optionally writes to BigQuery tables (when `--export-bigquery` is used or when `export-bq` is called). The enriched DataFrame (previously in-memory only) is now also saved to `data/output/universities.{csv,parquet}`. BigQuery write is best-effort for `run --export-bigquery`, hard-fail for `export-bq`.
- `etl-cli`: New `export-bq` subcommand added. The `run` command defaults to local-only output; `--export-bigquery` / `--export-bq` flag enables BigQuery upload. The `extract` and `view` commands are unaffected.

## Impact

- **Dependencies**: New: `google-cloud-bigquery`. No removals.
- **Source files**: New file `src/load/bigquery.py`; modified `src/load/__init__.py`, `src/pipeline/run.py`, `src/cli.py`, `pyproject.toml`.
- **Configuration**: New env vars `GOOGLE_CLOUD_PROJECT`, `GOOGLE_BIGQUERY_DATASET`, `GOOGLE_APPLICATION_CREDENTIALS` (standard ADC). Optional `.env` support via `python-dotenv` (already a dev dep).
- **External systems**: Requires GCP project with BigQuery API enabled, a service account with `bigquery.dataEditor` and `bigquery.jobUser` roles, and valid ADC.
- **Breaking changes**: None. All existing commands, output files, and APIs remain unchanged. New files `data/output/universities.{csv,parquet}` created alongside existing outputs.
