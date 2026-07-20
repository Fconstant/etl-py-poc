# bigquery-config Specification

## Purpose

Define how the ETL pipeline discovers and validates GCP BigQuery configuration, including project ID, dataset ID, and credentials. Configuration is sourced from environment variables with `.env` file support via `python-dotenv`.

## ADDED Requirements

### Requirement: Read GCP project ID from environment

The system SHALL read the GCP project ID from the `GOOGLE_CLOUD_PROJECT` environment variable.

#### Scenario: Project ID set
- **WHEN** `GOOGLE_CLOUD_PROJECT` is set to `my-gcp-project`
- **THEN** the BigQuery client targets `my-gcp-project`

#### Scenario: Project ID missing during BigQuery operation
- **WHEN** `GOOGLE_CLOUD_PROJECT` is not set and a BigQuery operation is attempted (via `--export-bigquery` or `export-bq`)
- **THEN** a clear error message is logged: "GOOGLE_CLOUD_PROJECT environment variable is not set. Set it and try again."

#### Scenario: Project ID missing, no BigQuery operation
- **WHEN** `GOOGLE_CLOUD_PROJECT` is not set but user runs `etl run` without `--export-bigquery`
- **THEN** no error or warning is produced; pipeline runs local-only normally

### Requirement: Read BigQuery dataset ID from environment

The system SHALL read the BigQuery dataset ID from the `GOOGLE_BIGQUERY_DATASET` environment variable, defaulting to `etl_universities` if not set.

#### Scenario: Custom dataset ID
- **WHEN** `GOOGLE_BIGQUERY_DATASET` is set to `etl_dev`
- **THEN** tables are written to the `etl_dev` dataset

#### Scenario: Default dataset ID
- **WHEN** `GOOGLE_BIGQUERY_DATASET` is not set
- **THEN** the dataset defaults to `etl_universities`

### Requirement: Application Default Credentials support

The system SHALL authenticate to GCP using Application Default Credentials (ADC), as implemented by the `google-cloud-bigquery` client library. No explicit credential file path is required in application code.

#### Scenario: ADC via service account key file
- **WHEN** `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to a valid service account JSON key file
- **THEN** the BigQuery client authenticates successfully using that service account

#### Scenario: ADC via gcloud CLI
- **WHEN** the user has run `gcloud auth application-default login` and `GOOGLE_APPLICATION_CREDENTIALS` is NOT set
- **THEN** the BigQuery client authenticates using the user's gcloud credentials

#### Scenario: No credentials available
- **WHEN** no ADC source is configured (no env var, no gcloud login) and a BigQuery operation is attempted
- **THEN** BigQuery operations fail with an authentication error, which is caught and logged as a warning (for `run --export-bigquery`) or raised as `RuntimeError` (for `export-bq`)

### Requirement: Configuration loaded lazily

The system SHALL load and validate BigQuery configuration only when a BigQuery operation is first attempted. Module import SHALL NOT trigger config validation. This allows `etl run` (default, no flag) to complete without any GCP env vars set.

#### Scenario: Config loaded on first BigQuery call
- **WHEN** `to_bigquery()` is called for the first time during `run --export-bigquery`
- **THEN** the config module reads env vars and validates them

#### Scenario: No config read during local-only run
- **WHEN** `etl run` executes without `--export-bigquery`
- **THEN** no GCP env vars are read and no BigQuery client is created

### Requirement: .env file support

The system SHALL load environment variables from a `.env` file in the project root, using `python-dotenv` (already a project dependency), before any BigQuery configuration is read.

#### Scenario: .env file with BigQuery vars
- **WHEN** `.env` contains `GOOGLE_CLOUD_PROJECT=my-project` and `GOOGLE_BIGQUERY_DATASET=etl_test`
- **THEN** those values are used as if they were set in the shell environment

#### Scenario: No .env file
- **WHEN** `.env` file does not exist
- **THEN** `load_dotenv()` is a no-op and the system reads from the actual environment
