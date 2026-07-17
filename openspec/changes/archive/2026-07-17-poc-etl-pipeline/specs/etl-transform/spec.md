## ADDED Requirements

### Requirement: Normalize country names via fuzzy matching
The system SHALL resolve inconsistent country names between the REST Countries API and Universities API using `difflib.get_close_matches()` from the Python standard library, with a cutoff threshold of 0.8.

#### Scenario: Exact match
- **WHEN** a university's `country` field matches a REST Countries `name` field exactly
- **THEN** no fuzzy matching is needed; the match is direct

#### Scenario: Fuzzy match
- **WHEN** a university's `country` is "United States" and the REST Countries name is "United States of America"
- **THEN** `get_close_matches("United States", ["United States of America", ...])` returns "United States of America"

#### Scenario: No match found
- **WHEN** a university's `country` has no close match above the cutoff threshold in the countries dataset
- **THEN** the university is excluded from the join result and a warning is logged with the unmatched country name

### Requirement: Join universities with countries
The system SHALL perform an inner join between the universities DataFrame and the normalized countries DataFrame using the country name as the join key.

#### Scenario: Successful join
- **WHEN** both DataFrames are available and country names are normalized
- **THEN** the result is a single Polars DataFrame with all university columns plus matching country columns

#### Scenario: Empty universities DataFrame
- **WHEN** the universities DataFrame is empty
- **THEN** the result is an empty DataFrame and a warning is logged

### Requirement: Enrich universities with country attributes
The system SHALL add country-level attributes (ISO code, continent, population, currency) to each university row after the join.

#### Scenario: Enriched record
- **WHEN** join succeeds for a university
- **THEN** the output row contains: university name, country name, ISO code, continent, population, currency

#### Scenario: Multiple universities in same country
- **WHEN** multiple universities exist in the same country
- **THEN** each university row independently carries the same country attributes

### Requirement: Transform functions are pure and composable
All transform functions SHALL be pure functions: `transform(df: pl.DataFrame) -> pl.DataFrame`. They SHALL NOT mutate input DataFrames and SHALL NOT have side effects.

#### Scenario: Pure transform
- **WHEN** calling `normalize(df)` on a copy
- **THEN** the original DataFrame is unchanged

#### Scenario: Composable pipeline
- **WHEN** calling `enrich(join_data(normalize_countries(df_c), normalize_universities(df_u)))`
- **THEN** the output is a fully enriched DataFrame without intermediate state or global variables