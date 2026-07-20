## 1. Dependencies Setup

- [x] 1.1 Add `google-cloud-bigquery>=3.27.0` to `[project.dependencies]` in `pyproject.toml`
- [x] 1.2 Run `uv lock` to resolve and pin new dependencies

## 2. BigQuery Configuration Module

- [x] 2.1 Create `src/load/config.py` with `BigQueryConfig` data class holding `project_id: str | None` and `dataset_id: str`
- [x] 2.2 Implement `get_bq_config()` function that reads `GOOGLE_CLOUD_PROJECT` and `GOOGLE_BIGQUERY_DATASET` (default `etl_universities`) from environment. Called lazily on first BigQuery operation (not at import time).
- [x] 2.3 Implement `is_bigquery_ready()` function that returns `True` only when `project_id` is set
- [x] 2.4 Log a single warning on first call when config is missing (not on every `to_bigquery` call)

## 3. BigQuery Loader Module

- [x] 3.1 Create `src/load/bigquery.py` with explicit `bigquery.SchemaField` definitions for all 4 tables per ADR-002
- [x] 3.2 Implement `_get_or_create_dataset(client, dataset_id)` — creates dataset if missing (location `US`)
- [x] 3.3 Implement `_get_or_create_table(client, dataset_id, table_id, schema)` — creates table with explicit schema if missing; catches `Conflict` (409) and continues
- [x] 3.4 Implement `to_bigquery(df: pl.DataFrame, table_name: str) -> bool`:
  - Guard: return `False` early if `is_bigquery_ready()` is `False`
  - Wrap all BQ operations in try/except, log warning on failure, return `False`
  - On success, return `True`
  - Serialize DataFrame to in-memory Parquet via `BytesIO` + `df.write_parquet(buf)`
  - Load into BigQuery via `client.load_table_from_file(buf, table_ref, job_config=LoadJobConfig(source_format="PARQUET", write_disposition="WRITE_TRUNCATE"))`
  - Ensure dataset and table exist before load
- [x] 3.5 Export `to_bigquery` from `src/load/__init__.py`

## 4. Pipeline — Enriched DataFrame Local Save

- [x] 4.1 Include enriched DataFrame in the `for df, name` loop in `src/pipeline/run.py`:
  ```python
  for df, name in [
      (enriched, "universities"),
      (by_country, "universities_per_country"),
      (by_continent, "universities_per_continent"),
      (top10, "top10_universities"),
  ]:
      to_csv(df, name)
      to_parquet(df, name)
  ```
- [x] 4.2 Verify `data/output/universities.csv` and `data/output/universities.parquet` are created after `etl run`

## 5. Pipeline — BigQuery Integration in `run` (opt-in)

- [x] 5.1 Import `to_bigquery` in `src/pipeline/run.py`
- [x] 5.2 Add `export_bigquery: bool = False` parameter to `run()` function signature
- [x] 5.3 In the `for df, name` loop, add `to_bigquery(df, name)` call after `to_csv`/`to_parquet` (only when `export_bigquery` is True)
- [x] 5.4 Print BigQuery load summary (tables written, or warnings) only when `export_bigquery` is True

## 6. CLI — `run` Command `--export-bigquery` Flag

- [x] 6.1 Add `export_bigquery: bool = typer.Option(False, "--export-bigquery", "--export-bq", help="Upload results to BigQuery")` to `run()` command in `src/cli.py`
- [x] 6.2 Pass `export_bigquery` through to `run_pipeline(export_bigquery=export_bigquery)`

## 7. CLI — New `export-bq` Command

- [x] 7.1 Create `src/pipeline/export_bq.py` with `export_to_bigquery() -> None` function:
  - Read 4 Parquet files from `data/output/` via `pl.read_parquet()`
  - Raise `FileNotFoundError` with clear message if any file missing
  - Call `to_bigquery(df, table_name)` for each — check return value
  - Raise `RuntimeError` if any `to_bigquery()` call returns `False`
  - Print success summary on completion
- [x] 7.2 Register `@app.command()` decorator for `export_bq()` in `src/cli.py` calling `export_to_bigquery()`
- [x] 7.3 Wire up: `etl export-bq` shows in help output and executes correctly

## 8. Tests

- [x] 8.1 Create `tests/test_bigquery_config.py`:
  - Test `get_bq_config()` reads env vars correctly
  - Test `is_bigquery_ready()` returns True/False based on `GOOGLE_CLOUD_PROJECT` presence
  - Test default `dataset_id` is `etl_universities`
- [x] 8.2 Create `tests/test_bigquery_loader.py`:
  - Test `to_bigquery()` returns `False` (no-op) when config missing
  - Test `to_bigquery()` returns `False` and logs warning on exception
  - Test `to_bigquery()` returns `True` on successful write
  - Test Parquet serialization roundtrip (write to BytesIO, read back, verify shape/columns)
  - Test table name mapping (aggregate names → BQ table names)
  - Use `unittest.mock.patch` for `google.cloud.bigquery.Client` — no real GCP calls
- [x] 8.3 Create `tests/test_export_bq.py`:
  - Test `export_to_bigquery()` raises `FileNotFoundError` when `data/output/universities.parquet` is missing
  - Test `export_to_bigquery()` raises `RuntimeError` when `to_bigquery()` returns `False`
  - Test `export_to_bigquery()` completes successfully when all files present and writes succeed
  - Mock `pl.read_parquet()` and `to_bigquery()` — no real I/O
- [x] 8.4 Update existing pipeline tests:
  - Test `run()` default behavior: local-only output, no BigQuery calls
  - Test `run(export_bigquery=True)` calls `to_bigquery` for all 4 DataFrames
  - Test enriched DataFrame appears in local output files

## 9. Documentation

- [x] 9.1 Update `README.md`:
  - Add BigQuery setup section (GCP project, service account, ADC, env vars)
  - Document `etl export-bq` command
  - Document `--export-bigquery` flag on `etl run`
  - Add BigQuery output to pipeline overview diagram/description
  - Document new output files: `data/output/universities.{csv,parquet}`

## 10. Quality Gates

- [x] 10.1 Run `uv run ruff check .` — fix any lint issues
- [x] 10.2 Run `uv run ruff format --check .` — ensure formatting is clean
- [x] 10.3 Run `uv run pyright` — ensure strict typechecking passes
- [x] 10.4 Run `uv run pytest` — all tests pass (existing + new)
- [x] 10.5 Verify all type annotations present (pyright strict mode)
