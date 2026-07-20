# bigquery-load Specification

## Purpose

Define the BigQuery output capability for the ETL pipeline. Writes enriched raw data and aggregated results to BigQuery tables using Google Cloud BigQuery client library with WRITE_TRUNCATE disposition. Used by both `etl run --export-bigquery` (best-effort) and `etl export-bq` (hard-fail).

## ADDED Requirements

### Requirement: Write enriched data to BigQuery

The system SHALL write the enriched DataFrame (university name, country, ISO code, continent, population, currency name) to the BigQuery table `etl_universities.universities` using `WRITE_TRUNCATE` write disposition.

#### Scenario: Successful enriched write
- **WHEN** a valid enriched DataFrame contains rows after the join and enrichment transforms
- **THEN** all rows are written to `etl_universities.universities`, overwriting any existing data in that table

#### Scenario: Empty enriched DataFrame
- **WHEN** the enriched DataFrame is empty (no universities matched any country)
- **THEN** the BigQuery table is truncated (all rows removed) and a warning is logged

### Requirement: Write aggregated results to BigQuery

The system SHALL write the three aggregated DataFrames to their corresponding BigQuery tables using `WRITE_TRUNCATE` write disposition:
- `universities_per_country` → `etl_universities.universities_per_country`
- `universities_per_continent` → `etl_universities.universities_per_continent`
- `top10_countries` → `etl_universities.top10_universities`

#### Scenario: All three aggregated tables written
- **WHEN** a BigQuery export operation is triggered with valid aggregated DataFrames
- **THEN** all three BigQuery tables are overwritten with the current aggregation results

#### Scenario: Aggregated DataFrame has fewer than 10 rows
- **WHEN** `top10_countries` returns fewer than 10 rows (fewer than 10 distinct countries)
- **THEN** all available rows are written to `etl_universities.top10_universities`

### Requirement: BigQuery table schema matches ADR-002

The system SHALL define BigQuery table schemas explicitly matching ADR-002:
- `universities`: university_name (STRING), country (STRING), iso_code (STRING), continent (STRING), population (INT64), currency_name (STRING)
- `universities_per_country`: country (STRING), university_count (INT64)
- `universities_per_continent`: continent (STRING), university_count (INT64)
- `top10_universities`: country (STRING), university_count (INT64)

#### Scenario: Schema verification
- **WHEN** inspecting the BigQuery table schema in GCP console
- **THEN** each table's column names and types match the ADR-002 specification exactly

### Requirement: Idempotent table creation

The system SHALL create the `etl_universities` dataset and all four tables if they do not exist. If the dataset or table already exists, the system SHALL proceed without error.

#### Scenario: First BigQuery write creates dataset and tables
- **WHEN** a BigQuery operation runs against a GCP project where `etl_universities` dataset does not exist
- **THEN** the dataset is created in the configured region (default: `US`), and all four tables are created with the explicit schemas before data is loaded

#### Scenario: Subsequent write skips creation
- **WHEN** a BigQuery operation runs and all tables already exist
- **THEN** no creation attempt is made; data is loaded into existing tables

#### Scenario: Partial existence
- **WHEN** some tables exist and others do not
- **THEN** only the missing tables are created; existing tables are left untouched

### Requirement: Parquet-based serialization

The system SHALL serialize Polars DataFrames to Parquet format in memory (BytesIO) and use `client.load_table_from_file()` with `source_format="PARQUET"` to load data into BigQuery.

#### Scenario: Type preservation
- **WHEN** a Polars DataFrame contains Int64, Float64, and String columns
- **THEN** after loading to BigQuery, column types are INT64, FLOAT64, and STRING respectively

#### Scenario: Null handling
- **WHEN** a field contains null values (e.g., currency_name for countries without currency)
- **THEN** null values are preserved as NULL in BigQuery, not coerced to empty strings or zero

### Requirement: to_bigquery() returns success indicator

The `to_bigquery()` function SHALL return `True` on successful write and `False` on failure, without raising exceptions. Callers decide the error policy: `etl run --export-bigquery` ignores the return value (best-effort), `etl export-bq` checks and raises on `False`.

#### Scenario: Write succeeds
- **WHEN** `to_bigquery(df, "universities")` completes without errors
- **THEN** the function returns `True`

#### Scenario: Write fails
- **WHEN** `to_bigquery(df, "universities")` encounters a network error or permission denied
- **THEN** the function logs a warning and returns `False`

### Requirement: Local files are primary, BigQuery is additive

The system SHALL always write all 4 DataFrames to local CSV/Parquet files in `data/output/`. BigQuery writes are opt-in and never replace or block local output.

#### Scenario: Local-only run (default)
- **WHEN** `etl run` executes without flags
- **THEN** all 4 DataFrames are written to `data/output/*.csv` and `data/output/*.parquet` (8 files); no BigQuery operations are attempted

#### Scenario: Run with BigQuery enabled
- **WHEN** `etl run --export-bigquery` executes with valid GCP credentials
- **THEN** data is written to both BigQuery tables (4 tables) AND local files (8 files)

#### Scenario: export-bq from local files
- **WHEN** `etl export-bq` executes with valid credentials and existing local Parquet files
- **THEN** DataFrames are loaded from `data/output/*.parquet` and uploaded to BigQuery tables; no local files are modified
