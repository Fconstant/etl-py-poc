# Delta: etl-transform

## MODIFIED Requirements

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

> Nota: o exemplo anterior da spec principal ("United States" → "United States of America", ratio 0.70) está abaixo do cutoff 0.8 e nunca casou via fuzzy — "United States" casa por match exato no dataset real.

#### Scenario: No match found
- **WHEN** a university's `country` has no exact, alias, or fuzzy match above the cutoff threshold
- **THEN** the university is excluded from the join result and a warning is logged with the unmatched country name

#### Scenario: Approximate alias accepted for DRC
- **WHEN** a university's `country` is "Congo, the Democratic Republic of the" and the countries dataset contains only "Congo" (Republic of the Congo, ISO CG)
- **THEN** the alias table maps it to "Congo" as a **deliberate approximation** — the dataset lacks a DR Congo entry, and keeping the rows (with CG attributes) was preferred over dropping them; revisit if the countries source ever includes DR Congo (ISO CD)
