## Why

After running `etl view` the user must manually open `data/output/report.html` in a browser. Auto-opening the report removes this friction — one command shows the result immediately, with zero extra steps.

## What Changes

- After generating the report, the `view` command opens `report.html` in the default browser via Python stdlib `webbrowser`
- Print message changes from "Report generated: data/output/report.html" to "Report opened in browser: data/output/report.html"
- No new dependencies — `webbrowser` is stdlib
- No changes to report generation logic — only the CLI command adds the browser-open step

## Capabilities

### New Capabilities

*(None)*

### Modified Capabilities

- `etl-view`: The `view` command behavior extends to auto-open the generated HTML report in the system's default browser after writing it to disk.

## Impact

- **CLI**: `view` command in `src/cli.py` adds `webbrowser.open()` call after `generate_report()` — one new import, one new line
- **Tests**: Integration test updated to mock `webbrowser.open` and verify it's called with the correct path
- **No changes** to `src/view/report.py`, README, or any other module
