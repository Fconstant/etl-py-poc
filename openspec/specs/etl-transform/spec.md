# etl-transform Specification

## Purpose
TBD - created by archiving change poc-etl-pipeline. Update Purpose after archive.
## Requirements
### Requirement: Normalize country names via fuzzy matching

The system SHALL resolve inconsistent country names between the REST Countries API and Universities API using, in order: exact match, an alias table loaded from `data/country_aliases.json` (mapping formal ISO 3166 names to REST Countries common names), and `difflib.get_close_matches()` (stdlib) with cutoff 0.8 as fallback. The alias file SHALL be versioned in git (`.gitignore` exception) and loaded by `normalize_universities` itself by default; an optional `aliases` parameter allows injecting the table (e.g., in tests) without touching disk.

#### Scenario: Exact match
- **WHEN** a university's `country` field matches a REST Countries `name` field exactly
- **THEN** the match is direct; no alias lookup or fuzzy matching is performed

#### Scenario: Alias match
- **WHEN** a university's `country` is "Russian Federation" and `data/country_aliases.json` maps it to "Russia", which exists in the countries dataset
- **THEN** the university is resolved to "Russia" without fuzzy matching

#### Scenario: Alias target absent from dataset
- **WHEN** an alias entry points to a name not present in the countries dataset
- **THEN** resolution falls through to fuzzy matching, and to the unmatched warning if that also fails

#### Scenario: Alias file missing or invalid
- **WHEN** `data/country_aliases.json` is missing or contains invalid JSON and `normalize_universities` is called without an explicit `aliases` argument
- **THEN** the pipeline fails fast with the standard `open`/`json.load` exception — the file is versioned, so absence indicates a broken checkout

#### Scenario: Aliases injected explicitly
- **WHEN** `normalize_universities` receives an explicit `aliases` dict (including an empty one)
- **THEN** the file is not read and the provided table is used as-is

#### Scenario: Fuzzy match fallback
- **WHEN** a university's `country` is "Turkiye" (no exact or alias match) and the REST Countries name is "Türkiye"
- **THEN** `get_close_matches("Turkiye", ["Türkiye", ...])` returns "Türkiye" (ratio 0.86 ≥ 0.8)

#### Scenario: No match found
- **WHEN** a university's `country` has no exact, alias, or fuzzy match above the cutoff threshold
- **THEN** the university is excluded from the join result and a warning is logged with the unmatched country name

#### Scenario: Approximate alias accepted for DRC
- **WHEN** a university's `country` is "Congo, the Democratic Republic of the" and the countries dataset contains only "Congo" (Republic of the Congo, ISO CG)
- **THEN** the alias table maps it to "Congo" as a **deliberate approximation** — the dataset lacks a DR Congo entry, and keeping the rows (with CG attributes) was preferred over dropping them; revisit if the countries source ever includes DR Congo (ISO CD)

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

