# etl-view Specification

## Purpose

Delta spec adding auto-open-browser behavior to the `etl view` command.

## ADDED Requirements

### Requirement: View command opens report in default browser

The system SHALL open the generated `report.html` in the user's default browser using Python stdlib `webbrowser.open()`. The file path SHALL be converted to a `file://` URI before opening.

#### Scenario: Report opens in browser
- **WHEN** `etl view` completes report generation successfully
- **THEN** `webbrowser.open()` is called with a `file://` URI pointing to `data/output/report.html`

#### Scenario: Browser unavailable
- **WHEN** `webbrowser.open()` returns `False` (no browser available, e.g., headless environment)
- **THEN** the system SHALL print a warning message with the file path and exit with code 0
