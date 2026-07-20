## Context

The ETL pipeline (POC maturity 2.5/5) currently writes output exclusively to local files (`data/output/*.csv`, `data/output/*.parquet`). ADR-001 defines a 3-phase GCP migration; Phase 1 (current) adds BigQuery as an output destination alongside existing local file output. ADR-002 defines the BigQuery data model (4 tables in `etl_universities` dataset, `WRITE_TRUNCATE` disposition, no partitioning/clustering). ADR-003 mandates keeping Polars transforms — BigQuery is output-only. ADR-004 defers app split to Phase 3; the CLI and module layout remain unchanged.

Current load layer (`src/load/loader.py`): two functions (`to_csv`, `to_parquet`) called from `src/pipeline/run.py` in a loop over 3 aggregated DataFrames. The enriched DataFrame (raw data) is currently NOT persisted — only aggregated outputs are saved. Per ADR-002, Phase 1 exposes all 4 DataFrames to BigQuery AND now also persists enriched locally for `export-bq` to consume.

## Goals / Non-Goals

**Goals:**
- Write 4 DataFrames (enriched raw + 3 aggregated) to BigQuery tables when requested
- `etl run` is local-only by default (zero network/GCP dependency); `--export-bigquery` flag opts into BigQuery upload
- `etl export-bq` command: reads local Parquet files and uploads to BigQuery (no re-pipeline, hard-fail)
- Save enriched DataFrame locally as `data/output/universities.{csv,parquet}` alongside existing 3 aggregated outputs
- Idempotent: first BigQuery write creates dataset and tables if missing; subsequent writes overwrite
- Credentials via GCP Application Default Credentials (standard for Cloud Run → Phase 3)
- Configuration via environment variables (project ID, dataset ID)
- BigQuery failures in `run --export-bigquery` are non-blocking: log warning, continue
- BigQuery failures in `export-bq` are blocking: raise exception with clear error

**Non-Goals:**
- Streaming or incremental writes (WRITE_TRUNCATE only)
- BigQuery partitions, clustering, or views
- SQL transforms or scheduled queries (Polars does transforms per ADR-003)
- GCS integration (Phase 2)
- Cloud Run deployment (Phase 3)
- App split into core/cli/server (Phase 3 per ADR-004)
- Removing or replacing local file output

## Decisions

### Decision 1: Polars → BigQuery via Parquet serialization

**Chosen**: Write DataFrame to in-memory Parquet buffer (`BytesIO`), then load into BigQuery using `client.load_table_from_file()` with `source_format="PARQUET"`.

**Rationale**:
- Parquet preserves type information better than CSV or JSON (int64 → INT64, float64 → FLOAT64, string → STRING, etc.)
- No pandas dependency — avoids the Polars→pandas→BigQuery roundtrip (pandas type coercion is lossy)
- `google-cloud-bigquery` natively supports Parquet source format
- Simple: Polars `.write_parquet(buf)` → `buf.seek(0)` → `load_table_from_file(buf, ...)`

**Alternatives considered**:
- *Polars→pandas→`load_table_from_dataframe`*: Adds implicit pandas dependency; pandas dtype mapping to BQ types is less predictable for int64 nullability. Rejected.
- *Polars→NDJSON→BQ*: JSON serialization loses type precision (all numbers become floats). Rejected.
- *Polars→Arrow IPC→BQ*: BQ doesn't support Arrow IPC as source format. Not viable.

### Decision 2: Explicit BigQuery schema, not autodetect

**Chosen**: Define BigQuery table schemas explicitly using `bigquery.SchemaField` in `src/load/bigquery.py`. On each write, check if table exists; if not, create it with the explicit schema. Table creation is idempotent (`.create_table()` raises `Conflict` if table already exists — catch and ignore).

**Rationale**:
- `autodetect=True` guesses types from data and can produce different schemas across runs
- Explicit schemas match ADR-002 exactly and are verifiable
- Simplified: 4 tables, 6 fields max, no complex types
- Table creation is cheap (metadata operation, not data operation)

### Decision 3: GCP config via env vars

**Chosen**: A `src/load/config.py` module reads `GOOGLE_CLOUD_PROJECT` and `GOOGLE_BIGQUERY_DATASET` environment variables at module load time. `GOOGLE_APPLICATION_CREDENTIALS` is consumed by the BigQuery client library automatically via ADC. `python-dotenv` (already a project dependency) is called in `cli.py` before any config reads, so `.env` files work transparently.

**Rationale**:
- No config file to maintain — env vars are the GCP standard (Cloud Run, Cloud Functions, ADC)
- `.env` already works via existing `load_dotenv()` in `cli.py`
- Optional: BigQuery config is only checked when `--export-bigquery` or `export-bq` is used; `run` without the flag works fine without any GCP env vars
- Simple: `os.environ.get("GOOGLE_CLOUD_PROJECT", "")` with clear error messages

### Decision 4: Best-effort BigQuery write in `run --export-bigquery`, hard-fail in `export-bq`

**Chosen**: `to_bigquery()` wraps BigQuery operations in `try/except` and returns `True` on success, `False` on failure. `etl run --export-bigquery` calls it and ignores failures (best-effort — BigQuery is additive). `etl export-bq` calls the same function but checks the return value and raises `RuntimeError` if any write fails (user explicitly asked to export, needs to know if it worked).

**Rationale**:
- Same code path, different error handling at call site — no duplicate logic
- `run --export-bigquery` should complete locally even if GCP fails (pipeline primary artifact is local files)
- `export-bq` exists specifically for BigQuery; failing silently would be confusing
- Clean separation: `to_bigquery()` provides the mechanism; callers decide the policy

**Alternatives considered**:
- *Strict mode parameter on `to_bigquery()`*: Adds boolean flag that changes behavior — subtle, easy to misuse. Return value + caller check is more explicit. Rejected.
- *Separate `to_bigquery_strict()` function*: Duplicates code. Rejected.

### Decision 5: Enriched DataFrame saved locally

**Chosen**: `src/pipeline/run.py` saves the enriched DataFrame to `data/output/universities.csv` and `data/output/universities.parquet` alongside the 3 aggregated outputs. Previously, enriched was only in-memory and written only to BigQuery.

**Rationale**:
- `etl export-bq` needs local files as data source — can't re-construct enriched from aggregated outputs
- Enriched data is valuable for local inspection (same value proposition as BigQuery raw table)
- Consistent: all 4 DataFrames are persisted locally AND optionally written to BigQuery
- Minimal cost: ~500KB extra disk for 10K rows in Parquet

**Alternatives considered**:
- *`export-bq` re-runs pipeline internally*: Duplicates transform logic, couples export to APIs/cache validity. Rejected.
- *`export-bq` only exports aggregated (skip enriched)*: Violates ADR-002. Rejected.

### Decision 6: CLI flag `--export-bigquery` on `run` command (opt-in)

**Chosen**: `etl run` writes local files only by default. Add `--export-bigquery` / `--export-bq` flag to also upload to BigQuery. `run_pipeline()` receives `export_bigquery: bool = False`. When `False`, no BigQuery operations are attempted (no config read, no client created). When `True`, calls `to_bigquery()` for all 4 DataFrames with best-effort error handling.

**Rationale**:
- Default local-only respects principle of least surprise — no network calls without explicit intent
- `etl run` works everywhere, immediately, with zero GCP setup
- Users who want BigQuery explicitly opt in per-invocation
- Consistent with `export-bq` command: both require explicit action for BigQuery

**Alternatives considered**:
- *`--skip-bigquery` (opt-out)*: Default BigQuery write breaks local-only workflows, surprises users without GCP creds. Rejected.
- *Two separate pipeline functions*: Duplicates extract/transform orchestration. Flag is cleaner. Rejected.

### Decision 7: New `etl export-bq` command

**Chosen**: A new Typer subcommand `export-bq` in `src/cli.py` that:
1. Reads the 4 Parquet files from `data/output/` (fail if any missing)
2. Calls `to_bigquery()` for each DataFrame
3. Raises `RuntimeError` if any BigQuery write fails (non-zero exit code)
4. Does NOT call `run_pipeline()` — pure read-from-disk → upload

**Rationale**:
- Re-exportable: fix credentials, re-run `export-bq` without re-running full pipeline
- Clean separation: `run` = pipeline (cache → transform → output), `export-bq` = disk → BQ
- Reuses `to_bigquery()` — no implementation duplication
- Command name `export-bq` is descriptive and distinct from `run`

**Alternatives considered**:
- *Flag on `run` to control BQ behavior*: `--export-bigquery` already exists for inline upload. Separate command is for re-export from disk. Different use cases. Rejected.

## Risks / Trade-offs

- **[Risk] BigQuery costs**: Each BigQuery upload executes 4 load jobs. At ~10K rows, free tier (10 GB/month storage, 1 TB/month queries) covers this completely. → **Mitigation**: Document costs in README; free tier is ample.
- **[Risk] Credential leakage**: GCP service account key in git if misconfigured. → **Mitigation**: `GOOGLE_APPLICATION_CREDENTIALS` points to a file outside the repo; `.gitignore` already has common patterns (`*.json` in root); README will document ADC setup.
- **[Risk] Parquet schema drift**: If Polars DataFrame schema changes, BigQuery table schema becomes stale and load job fails. → **Mitigation**: `WRITE_TRUNCATE` + explicit schema recreation on mismatch is not implemented (out of scope). Manual fix: drop and re-run.
- **[Risk] `export-bq` requires prior `run`**: New users might call `export-bq` without ever running the pipeline. → **Mitigation**: Clear error message: "File data/output/universities.parquet not found. Run `etl run` first."
- **[Risk] Network dependency is opt-in**: `etl run` has zero network dependency by default. Only `--export-bigquery` and `export-bq` require network. → **Mitigation**: Network failures in `--export-bigquery` are non-blocking; `export-bq` users expect network.
- **[Trade-off] Dual write is redundant**: When `--export-bigquery` is used, data exists in both local files and BigQuery. → Acceptable: Phase 1 is transitional; local files become optional in Phase 2 (GCS cache). Local files serve as offline backup and source for `export-bq`.
