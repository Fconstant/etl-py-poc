# Tasks: fix-country-name-aliases

## 1. Alias file + gitignore

- [x] 1.1 Create `data/country_aliases.json` with the 19 entries from design.md (includes DRC → Congo approximation)
- [x] 1.2 Add `!data/country_aliases.json` exception to `.gitignore`

## 2. Resolution order

- [x] 2.1 Add `load_country_aliases(path) -> dict[str, str]` to `src/transform/normalize.py` (stdlib `json.load`, fail fast on missing/invalid file)
- [x] 2.2 Update `normalize_universities(df, country_names, aliases)` and `_resolve` to: exact match → alias lookup (only if target exists in `country_names`) → fuzzy fallback (cutoff 0.8 unchanged)
- [x] 2.3 `normalize_universities` loads the JSON by default (`aliases=None` → `load_country_aliases()`); `run.py` unchanged from 2-arg call
- [x] 2.4 Keep the unmatched-countries warning as-is

## 3. Tests

- [x] 3.1 Test alias hit: "Russian Federation" resolves to "Russia"
- [x] 3.2 Test fuzzy fallback still works: "Turkiye" → "Türkiye" (ratio 0.86; original spec example "United States" → "United States of America" is 0.70, below cutoff)
- [x] 3.3 Test DRC approximate alias: "Congo, the Democratic Republic of the" → "Congo" (deliberate approximation; dataset lacks DR Congo)
- [x] 3.4 Test alias target absent from dataset falls through (no KeyError, no wrong match)
- [x] 3.5 Test `load_country_aliases` reads the shipped JSON into a `dict[str, str]`

## 4. Verify

- [x] 4.1 `uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest`
- [x] 4.2 `uv run etl run` — unmatched-countries warning eliminated (19 → 0; DRC covered by approximate alias)
