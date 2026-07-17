## 1. Project Setup

- [ ] 1.1 Create directory structure: `src/{extract,transform,load,pipeline,models,utils}`
- [ ] 1.2 Add `data/output/*.csv` and `data/output/*.parquet` to `.gitignore`

## 2. Utils

- [ ] 2.1 Implement `src/utils/log.py`: central `setup_logging()` function
- [ ] 2.2 Implement `src/utils/http.py`: httpx client factory with timeout and retry config

## 3. Models

- [ ] 3.1 Implement `src/models/country.py`: Pydantic `CountryModel` with fields `name`, `iso_code`, `continent`, `population`, `currency_name` and `Extra.ignore`
- [ ] 3.2 Implement `src/models/university.py`: Pydantic `UniversityModel` with fields `name`, `country`, `state_province`, `domains`, `web_pages` and `Extra.ignore`

## 4. Extract

- [ ] 4.1 Implement `src/extract/fetch_countries.py`: `fetch_countries()` — fetch, Pydantic parse, return Polars DataFrame
- [ ] 4.2 Implement `src/extract/fetch_universities.py`: `fetch_universities()` — fetch, Pydantic parse, return Polars DataFrame

## 5. Transform

- [ ] 5.1 Implement `src/transform/normalize.py`: `normalize_countries(df)`, `normalize_universities(df)` with `difflib.get_close_matches()` fuzzy matching (cutoff 0.8)
- [ ] 5.2 Implement `src/transform/join_data.py`: `join_data(universities, countries)` inner join on country name
- [ ] 5.3 Implement `src/transform/enrich.py`: `enrich(df)` selecting and renaming final columns
- [ ] 5.4 Implement `src/transform/aggregate.py`: `universities_per_country(df)`, `universities_per_continent(df)`, `top10_countries(df)`

## 6. Load

- [ ] 6.1 Implement `src/load/loader.py`: `to_csv(df, path)` and `to_parquet(df, path)` with auto-create output dir

## 7. Pipeline

- [ ] 7.1 Implement `src/pipeline/run.py`: `run()` function composing extract → transform → aggregate → load

## 8. CLI

- [ ] 8.1 Implement `main.py`: Typer app with `run` command
- [ ] 8.2 Add `[project.scripts]` entry point for `etl` in `pyproject.toml`

## 9. Docs

- [ ] 9.1 Write README.md with project overview, setup instructions, and usage examples
