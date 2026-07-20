# etl-view Specification

## Purpose

Provide a CLI command that reads the three pipeline output CSVs and generates a self-contained HTML report page for quick visual inspection.

## ADDED Requirements

### Requirement: CLI command registers `view` subcommand

The system SHALL expose a `view` subcommand on the existing Typer app, registered under `etl view`.

#### Scenario: Command exists
- **WHEN** user runs `etl view --help`
- **THEN** the output lists `view` as an available command with a description

### Requirement: Read CSVs from output directory

The system SHALL read the three CSV files produced by the pipeline from `data/output/`: `universities_per_country.csv`, `universities_per_continent.csv`, `top10_universities.csv`.

#### Scenario: CSVs exist
- **WHEN** all three CSV files are present in `data/output/`
- **THEN** they are loaded into Polars DataFrames without error

#### Scenario: Missing CSV
- **WHEN** any of the three CSV files is missing
- **THEN** the system SHALL raise a `FileNotFoundError` with a clear message indicating which file is missing

#### Scenario: Empty CSV
- **WHEN** a CSV file exists but is empty
- **THEN** the system SHALL render an empty table with a "No data" indicator rather than failing

### Requirement: Generate standalone HTML report

The system SHALL generate a single HTML file at `data/output/report.html` containing all three datasets rendered as HTML tables with inline CSS styling.

#### Scenario: Report generated
- **WHEN** `etl view` completes successfully
- **THEN** `data/output/report.html` exists and is a valid HTML document

#### Scenario: Self-contained
- **WHEN** inspecting `report.html`
- **THEN** all CSS is inline in a `<style>` tag and no external resources (fonts, images, scripts) are referenced

#### Scenario: Three tables present
- **WHEN** inspecting `report.html`
- **THEN** the page contains exactly three `<table>` elements, one per dataset, each preceded by an `<h2>` heading derived from the filename

### Requirement: Use tabulate for HTML table generation

The system SHALL use the `tabulate` library's `tablefmt="html"` to convert Polars DataFrame rows into valid, escaped HTML `<table>` elements. `tabulate` SHALL be the only new runtime dependency added.

#### Scenario: Tabulate added to dependencies
- **WHEN** inspecting `pyproject.toml` after implementation
- **THEN** `tabulate` appears in `[project.dependencies]` and no other new third-party package is added

#### Scenario: HTML escaping
- **WHEN** a data cell contains `<script>alert(1)</script>` or similar HTML
- **THEN** tabulate escapes the content so it renders as literal text, not executable markup

### Requirement: HTML formatting produces readable tables

The HTML SHALL include styling for readability: collapsed borders, alternating row background colors, bold headers, and padding on cells.

#### Scenario: Styled table headers
- **WHEN** inspecting the generated HTML
- **THEN** `<th>` elements have a distinct background color and bold font weight

#### Scenario: Alternating rows
- **WHEN** inspecting the generated HTML
- **THEN** even and odd `<tr>` rows have slightly different background colors for visual separation
