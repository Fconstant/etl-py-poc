# etl-aggregate-load Specification

## Purpose
TBD - created by archiving change poc-etl-pipeline. Update Purpose after archive.
## Requirements
### Requirement: Aggregate universities per country
The system SHALL compute the count of universities per country from the enriched DataFrame.

#### Scenario: Basic aggregation
- **WHEN** the enriched DataFrame contains 10 universities across 3 countries
- **THEN** the result is a DataFrame with columns `country` and `university_count` containing exactly 3 rows

#### Scenario: Country with no universities
- **WHEN** a country in the DataFrame has zero universities
- **THEN** it is excluded from the aggregation result

### Requirement: Aggregate universities per continent
The system SHALL compute the count of universities per continent from the enriched DataFrame.

#### Scenario: Continental breakdown
- **WHEN** the enriched DataFrame has universities in Europe and South America
- **THEN** the result is a DataFrame with columns `continent` and `university_count`

### Requirement: Top 10 countries by university count
The system SHALL produce a DataFrame of the top 10 countries ranked by university count (descending).

#### Scenario: More than 10 countries
- **WHEN** the enriched DataFrame has universities in more than 10 distinct countries
- **THEN** the result is a DataFrame with exactly 10 rows sorted by `university_count` descending

#### Scenario: Fewer than 10 countries
- **WHEN** fewer than 10 distinct countries have universities
- **THEN** the result contains all available countries

### Requirement: Load results to disk
The system SHALL write all aggregation results to `data/output/<filename>.csv` and `data/output/<filename>.parquet`.

#### Scenario: CSV output
- **WHEN** aggregations complete
- **THEN** files `data/output/universities_per_country.csv`, `data/output/universities_per_continent.csv`, `data/output/top10_universities.csv` are created

#### Scenario: Parquet output
- **WHEN** aggregations complete
- **THEN** corresponding `.parquet` files are created alongside CSV files

#### Scenario: Output directory missing
- **WHEN** `data/output/` does not exist
- **THEN** the system creates the directory before writing

### Requirement: CLI orchestration via Typer
The system SHALL expose a Typer CLI with a `run` command that executes the full pipeline.

#### Scenario: Run pipeline
- **WHEN** user executes `etl run`
- **THEN** the full pipeline (extract → transform → aggregate → load) executes and prints a summary to stdout

