## 1. Setup

- [x] 1.1 Add tabulate dependency: `uv add tabulate`

## 2. View module — HTML report generation

- [x] 2.1 Create `src/view/__init__.py` (empty)
- [x] 2.2 Create `src/view/report.py` with function `generate_report(output_dir: str = "data/output") -> None` that reads the three CSVs via Polars and writes `report.html`
- [x] 2.3 Implement helper `_df_to_html_table(df: pl.DataFrame, title: str) -> str` that converts a DataFrame to an HTML `<table>` via `tabulate(tablefmt="html")` and wraps it in a full page with inline CSS styling (collapsed borders, alternating rows, bold headers, cell padding)
- [x] 2.4 Handle missing CSV gracefully — raise `FileNotFoundError` with a clear message identifying which file is absent
- [x] 2.5 Handle empty CSV — render a "No data" row instead of an empty table

## 3. CLI integration

- [x] 3.1 Register `view` command on the Typer app in `src/cli.py` — import `generate_report` from `src.view.report` and wire to a `view` function that calls it

## 4. Tests

- [x] 4.1 Unit test `_df_to_html_table` returns valid HTML document with correct column headers and data rows
- [x] 4.2 Unit test `generate_report` writes `report.html` at the expected path
- [x] 4.3 Test missing CSV raises `FileNotFoundError` with expected message
- [x] 4.4 Test empty DataFrame renders a "No data" indicator row
- [x] 4.5 Integration test: run `etl view` via Typer CliRunner and verify `report.html` is created

## 5. Documentation

- [x] 5.1 Add `uv run etl view` to README usage section
- [x] 5.2 List `data/output/report.html` in the README outputs list

## 6. Verification

- [x] 6.1 Run full pipeline (`uv run etl run`), then `uv run etl view`, open `data/output/report.html` in browser to confirm three tables render correctly
- [x] 6.2 `uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest` — all pass
