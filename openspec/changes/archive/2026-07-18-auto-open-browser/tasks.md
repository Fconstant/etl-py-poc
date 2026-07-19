## 1. Implementation

- [x] 1.1 Import `webbrowser` in `src/cli.py`
- [x] 1.2 Modify `view` command: call `webbrowser.open(f"file://{resolved_path}")` after `generate_report()`, print success/warning message

## 2. Tests

- [x] 2.1 Update integration test in `tests/test_view.py` — mock `webbrowser.open` and verify called with correct `file://` URI
- [x] 2.2 Add test: when `webbrowser.open` returns `False`, command still exits 0 and prints warning

## 3. Verification

- [x] 3.1 `uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest` — all pass
