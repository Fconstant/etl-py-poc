# etl-extract Specification

## Purpose
TBD - created by archiving change poc-etl-pipeline. Update Purpose after archive.
## Requirements
### Requirement: Fetch countries from REST Countries API
The system SHALL fetch country data from `https://restcountries.com/v3.1/all` using httpx with a default timeout of 10 seconds and up to 3 retries on transient errors.

#### Scenario: Successful fetch
- **WHEN** the API responds with HTTP 200
- **THEN** raw JSON is returned as a list of country dicts

#### Scenario: API timeout
- **WHEN** the API does not respond within 10 seconds
- **THEN** the system retries up to 3 times with exponential backoff before raising a `RuntimeError`

#### Scenario: API returns 5xx
- **WHEN** the API returns HTTP 500, 502, or 503
- **THEN** the system retries up to 3 times before raising a `RuntimeError`

#### Scenario: API returns 4xx
- **WHEN** the API returns HTTP 404 or 429
- **THEN** the system raises an error immediately without retrying

### Requirement: Fetch universities from Universities API
The system SHALL fetch university data from `http://universities.hipolabs.com/search` using httpx with the same timeout and retry strategy.

#### Scenario: Successful fetch
- **WHEN** the API responds with HTTP 200
- **THEN** raw JSON is returned as a list of university dicts

#### Scenario: Connection refused
- **WHEN** the API host is unreachable
- **THEN** the system logs a warning and raises a `RuntimeError`

### Requirement: Parse raw JSON into flat typed models
The system SHALL validate and flatten nested JSON from both APIs using Pydantic `BaseModel` classes defined in `src/models/`.

#### Scenario: Countries JSON parsed
- **WHEN** raw country JSON is received
- **THEN** each country is validated and flattened into a model with fields: `name`, `iso_code`, `continent`, `population`, `currency_name`

#### Scenario: Universities JSON parsed
- **WHEN** raw university JSON is received
- **THEN** each university is validated and flattened into a model with fields: `name`, `country`, `state_province`, `domains`, `web_pages`

#### Scenario: Invalid JSON rejected
- **WHEN** a country entry is missing the required `name` field
- **THEN** Pydantic raises `ValidationError` and the entry is skipped with a warning logged

