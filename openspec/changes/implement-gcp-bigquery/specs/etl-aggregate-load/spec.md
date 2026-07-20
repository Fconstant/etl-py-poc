# etl-aggregate-load Delta Specification

## MODIFIED Requirements

### Requirement: Load results to disk
The system SHALL write all results — enriched raw data AND the three aggregated DataFrames — to `data/output/<filename>.csv` and `data/output/<filename>.parquet` on every `run`. BigQuery writes are opt-in via `--export-bigquery` flag (best-effort: failures logged, pipeline continues) or via `etl export-bq` command (hard-fail: errors raised). BigQuery writes SHALL use `WRITE_TRUNCATE` disposition.

#### Scenario: CSV output for all 4 DataFrames
- **WHEN** the pipeline completes (enrichment + aggregation)
- **THEN** files `data/output/universities.csv`, `data/output/universities_per_country.csv`, `data/output/universities_per_continent.csv`, `data/output/top10_universities.csv` are created

#### Scenario: Parquet output for all 4 DataFrames
- **WHEN** the pipeline completes
- **THEN** corresponding `.parquet` files are created alongside CSV files

#### Scenario: Enriched data saved locally
- **WHEN** the enrichment transform completes
- **THEN** the enriched DataFrame (columns: university_name, country, iso_code, continent, population, currency_name) is saved as `data/output/universities.csv` and `data/output/universities.parquet`

#### Scenario: Default run is local-only
- **WHEN** the user executes `etl run` without flags
- **THEN** only local CSV/Parquet files are written (8 files); no BigQuery operations are attempted

#### Scenario: BigQuery output with --export-bigquery flag
- **WHEN** the pipeline runs with `--export-bigquery` flag and GCP credentials are configured
- **THEN** all 4 DataFrames are written to both local files AND BigQuery tables

#### Scenario: BigQuery failure does not block local files (run --export-bigquery)
- **WHEN** BigQuery write fails during `etl run --export-bigquery` (network error, permission denied, or missing credentials)
- **THEN** a warning is logged and local CSV/Parquet files are still written successfully

#### Scenario: Output directory missing
- **WHEN** `data/output/` does not exist
- **THEN** the system creates the directory before writing

#### Scenario: export-bq reads from local files
- **WHEN** `etl export-bq` is executed with valid credentials and all 4 Parquet files present in `data/output/`
- **THEN** DataFrames are loaded from the Parquet files and uploaded to their corresponding BigQuery tables
