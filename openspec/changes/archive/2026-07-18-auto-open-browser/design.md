## Context

The `etl view` command (from `add-view-cli` change) generates `data/output/report.html` and prints a message. The user must then manually locate and open the file. Python stdlib's `webbrowser` module can open files in the default browser — zero new dependencies.

Current flow: `view` command → `generate_report()` → prints path → done.

Target flow: `view` command → `generate_report()` → `webbrowser.open()` → prints confirmation.

## Goals / Non-Goals

**Goals:**
- After generating `report.html`, open it automatically in the system's default browser
- No new dependencies — `webbrowser` is stdlib
- Graceful degradation — if browser can't open, still print the file path for manual access
- Minimal change — one import, one `webbrowser.open()` call in `cli.py`

**Non-Goals:**
- Any changes to `src/view/report.py` (generation logic stays untouched)
- Opening specific browsers (Firefox, Chrome) — use system default
- Live-reload or auto-refresh on pipeline re-run
- Terminal fallback for headless environments

## Decisions

1. **Open in CLI, not in `generate_report()`** — `generate_report` stays a pure function that only writes files. The browser-open concern belongs to the CLI, which orchestrates user-facing behavior.

2. **`webbrowser.open(f"file://{resolved_path}")`** — `webbrowser.open()` with a `file://` URI works cross-platform. Using `pathlib.Path.resolve()` ensures an absolute path, avoiding issues with relative paths.

3. **Non-fatal failure** — If `webbrowser.open()` returns `False` (e.g., headless environment, no DISPLAY), the command continues and prints the file path. User can still open manually. No exception raised.

4. **Print message says "opened in browser"** — replaces old "Report generated" message. If open fails, prints a warning + path.

## Risks / Trade-offs

- **[Headless/CI environment]** → `webbrowser.open()` returns `False`. Print warning + path instead of failing. Acceptable trade-off.
- **[Security: file:// URI]** → Only opens local files we just wrote. No user input involved in the path. Low risk.
- **[No browser installed]** → Same as headless — returns `False`, prints path. User sees the message and opens manually.
