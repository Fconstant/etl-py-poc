# ADR-004: Defer App Split — CLI Only for Now

**Date:** 2026-07-19
**Status:** Proposed
**Deciders:** diplo
**Related:** ADR-001 (Phase 3)

## Context

To serve the pipeline via HTTP (Cloud Run), the app needs a server interface (FastAPI/Flask) alongside the CLI. This requires splitting `src/` into core (business logic) and interfaces (cli, server).

## Decision

**Defer the app split.** Keep the current structure with CLI only. Split when Phase 3 (Cloud Run) begins.

### Current structure (kept)

```
src/
├── cli.py              # Typer interface + orchestration
├── pipeline/run.py     # Core pipeline
├── extract/            # Core
├── transform/          # Core
├── load/               # Core (BigQuery added here)
├── models/             # Core
├── view/               # Output generation
└── utils/              # Shared
```

### Future structure (Phase 3)

```
src/
├── core/               # Business logic, no framework dependency
│   ├── extract/
│   ├── transform/
│   ├── load/
│   ├── pipeline/
│   └── models/
├── interfaces/
│   ├── cli/            # Typer app → calls core
│   └── server/         # FastAPI app → calls core
└── utils/
```

## Rationale

**Why defer:**
- Phase 1 (BigQuery) doesn't require the split
- Premature abstraction adds complexity without value
- The current `pipeline/run.py` is already a clean composition root
- Splitting now would mean moving files around without functional benefit

**Why split later (Phase 3):**
- Cloud Run needs an HTTP endpoint (FastAPI)
- CLI and server share the same core logic
- Clean separation avoids duplicating orchestration calls

**The key insight:** `pipeline/run.py` is already the "core" — it's a pure function composition. The split is just moving it into a `core/` directory and making imports explicit.

## Consequences

- CLI remains the only interface for Phases 1-2
- `pipeline/run.py` stays as-is (already clean)
- When Phase 3 begins, the split is mechanical (move files, update imports)
- No FastAPI dependency until Phase 3

## References

- Current architecture: `src/pipeline/run.py` (39 lines, pure composition)
- Future: FastAPI for HTTP, Cloud Run for deployment
