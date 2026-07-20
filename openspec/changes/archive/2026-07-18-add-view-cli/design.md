## Context

Pipeline generates three CSVs in `data/output/`: `universities_per_country.csv`, `universities_per_continent.csv`, `top10_universities.csv`. No way to inspect them without opening CSV files. ADR 0001 (`docs/adr/0001-etl-view-cli-command.md`) already decided the approach: add `etl view` command generating a single static HTML page. Zero new deps was the original target, but `tabulate` (40KB, pure Python, MIT) handles HTML table generation more robustly — proper escaping, edge cases, no manual f-string construction.

Current CLI (`src/cli.py`) has `extract` and `run` commands. The project uses Typer for CLI, Polars for data, stdlib for file I/O. No HTML generation exists today.

## Goals / Non-Goals

**Goals:**
- New `etl view` Typer command reads the three CSVs and writes `data/output/report.html`
- HTML is self-contained (inline CSS) — single file to share, openable in any browser
- Use `tabulate` for HTML table generation (escaped, well-formed `<table>` element) + stdlib for page wrapper
- Minimal code surface — a thin function delegates table rendering to tabulate, keeping only CSS wrapper logic in our code
- Update README with `etl view` usage

**Non-Goals:**
- Interactive or dynamic HTML (charts, sorting, filtering)
- Terminal/ASCII rendering of tables
- Any changes to the existing pipeline stages (extract, transform, load)
- CSS framework or external assets

## Decisions

1. **Place new logic in `src/view/report.py`** — not inline in CLI. Keeps CLI thin (one new import + one command), makes the HTML-generation function independently testable.

2. **Polars `read_csv()` to load** — already a project dependency; no need for csv stdlib (which would require manual column handling).

3. **`tabulate` for HTML table rendering** — replaces hand-written f-string table builder. `tabulate(tablefmt="html")` generates a valid `<table>` with proper escaping, alignment markers, and `<thead>`/`<tbody>`. Tabulate is a 40KB pure-Python library with zero transitive dependencies and MIT license. We still own the full-page wrapper (`<!DOCTYPE html>`, `<html>`, `<head>`, `<style>`, `<body>`) via f-strings, which keeps control over layout and CSS. This is a better trade-off than full f-string tables (escaping risk, more code) or Jinja2 (heavy, overkill).

4. **Inline `<style>` block** — single file to share. CSS is minimal: font-family, border-collapse, alternating row colors, sticky headers.

5. **`pathlib` for file I/O** — consistent with the rest of the project (currently `os.path` in loader.py, but pathlib is stdlib and preferred for new code).

6. **Table titles as `<h2>` headings** — derived from the filename stem (e.g., "Universities Per Country").

## Risks / Trade-offs

- **[Large datasets]** → Mitigation: Current pipeline is small (hundreds of rows). If data grows, HTML file size grows linearly. Acceptable for POC.
- **[No-pager]** → Mitigation: All tables fit on one screen at current scale. Not a concern today.
- **[tabulate API change]** → Mitigation: Tabulate is stable (v0.10.0, 10+ years old). We only use `tabulate()` with `tablefmt="html"` — one of its most basic features, unlikely to break.
- **[Extra dependency]** → Mitigation: Tabulate is 40KB, pure Python, zero transitive deps. Negligible impact on install size or CI time.
