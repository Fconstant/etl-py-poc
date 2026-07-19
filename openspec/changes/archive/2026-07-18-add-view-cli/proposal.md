## Why

Pipeline output lives as CSV/Parquet files in `data/output/`. Inspecting them currently requires opening CSV files manually — inconvenient for quick checks and not shareable with non-devs. A single `etl view` command that generates a standalone HTML report makes output inspection instant and shareable.

## What Changes

- Add `view` subcommand to the existing Typer CLI (`src/cli.py`)
- Read the three CSVs (`universities_per_country.csv`, `universities_per_continent.csv`, `top10_universities.csv`) using Polars
- Generate a single static HTML page (`data/output/report.html`) with all three tables stacked, inline CSS
- Zero new dependencies — Polars already in project, HTML built with f-strings, file I/O via stdlib pathlib
- Update README to document the new command

## Capabilities

### New Capabilities
- `etl-view`: CLI command that reads pipeline output CSVs and generates a self-contained HTML report page with all three tables rendered in a clean, responsive layout.

### Modified Capabilities

- *(None — extract, transform, and aggregate-load specs unchanged)*

## Impact

- **CLI**: New `view` command registered in `src/cli.py`
- **New module**: Small `src/view/report.py` (or inline in cli) — a pure function `(universities_per_country_path, universities_per_continent_path, top10_path) -> str` that returns HTML string
- **Output**: `data/output/report.html` — standalone, no external CSS/JS dependencies
- **Dependencies**: No new packages; uses existing Polars + stdlib
