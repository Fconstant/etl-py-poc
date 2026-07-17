# AGENTS.md

Didactic ETL pipeline (REST Countries + Universities APIs) → Polars → CSV/Parquet. Python 3.12+, managed by `uv`. Target maturity 2.5/5: organized and extensible, no enterprise complexity.

## Commands

All Python runs through `uv run` (never bare `python`/`pip`):

```sh
uv run ruff check .          # lint
uv run ruff format .         # format
uv run pyright               # typecheck (strict mode)
uv run pytest                # all tests
uv run pytest tests/test_x.py::test_name   # single test
uv add <pkg> / uv add --dev <pkg>          # deps (updates uv.lock)
```

Before finishing any task: `uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest`.

## Typesafety (enforced by pyright strict + ruff ANN)

- Annotate every function signature, including `-> None`. Pyright strict fails otherwise.
- Modern syntax only: `list[str]`, `X | None` — never `List`, `Optional`.
- No `Any`, no bare `# type: ignore`. If truly unavoidable, use targeted `# pyright: ignore[ruleName]` with a reason.
- Pydantic v2 idioms: `model_config = ConfigDict(extra="ignore")` — NOT v1 `class Config` / `Extra.ignore` (some openspec docs use v1 syntax; ignore that).
- Polars DataFrames are untyped internally — validation happens once, via Pydantic at the extract boundary. Do not re-validate downstream.

## Architecture (decided in openspec/changes/poc-etl-pipeline/design.md)

- Pure functions per stage: `(DataFrame) -> DataFrame`. No stateful classes (no `ETLProcessor` etc.). Composition root is `src/pipeline/run.py`.
- Pydantic models only at extract boundary (`src/models/`); everything after is Polars.
- Prefer Polars lazy (`scan_*`, `LazyFrame`) until final `collect()`.
- Country-name normalization: stdlib `difflib.get_close_matches()` (cutoff 0.8) — no fuzzy-matching deps.
- CLI: Typer app in `main.py`, command `run`.
- Layout: `src/{extract,transform,load,pipeline,models,utils}` per design doc.

## Workflow

- Spec-driven via OpenSpec. Active change: `openspec/changes/poc-etl-pipeline/` (proposal, design, tasks, specs). Implement by following `tasks.md`; use the `openspec-apply-change` skill.
- Docs/specs are PT-BR; code, comments, and commits in English.
