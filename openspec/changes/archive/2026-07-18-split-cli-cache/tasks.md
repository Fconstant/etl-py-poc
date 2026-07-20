# Tasks: split-cli-cache

## 1. Módulo de cache

- [x] 1.1 Criar `src/extract/cache.py` com `CACHE_DIR = "data/cache"`, `TTL_SECONDS = 86400`, `save_cache(df: pl.DataFrame, name: str) -> None` (Parquet; ignora DataFrame vazio) e `load_cache(name: str) -> pl.DataFrame | None` (None se ausente, stale por mtime, ou leitura falha)
- [x] 1.2 Adicionar `get_countries() -> pl.DataFrame` e `get_universities() -> pl.DataFrame` em `src/extract/cache.py`: cache-first, fallback `fetch_*()` + `save_cache` (write-through)
- [x] 1.3 Testes de `cache.py`: hit dentro do TTL, miss por ausência, miss por expiração (mtime forjado com `os.utime`), miss por arquivo corrompido, vazio não gravado, `get_*` grava cache após fetch (fetch mockado)

## 2. CLI e pipeline

- [x] 2.1 Em `src/cli.py`: remover comando `start`; adicionar `extract()` (chama `fetch_countries`/`fetch_universities` + `save_cache`, sempre bate na API) e `run()` (chama pipeline)
- [x] 2.2 Em `src/pipeline/run.py`: trocar `fetch_countries()`/`fetch_universities()` por `get_countries()`/`get_universities()`
- [x] 2.3 Smoke test manual: `uv run etl extract` grava `data/cache/*.parquet`; `uv run etl run` na sequência não bate nas APIs; `uv run etl` sem subcomando mostra help

## 3. Housekeeping e docs

- [x] 3.1 Adicionar `data/cache/` ao `.gitignore`
- [x] 3.2 Atualizar `README.md`: seção Uso com `uv run etl extract` / `uv run etl run`, comportamento de cache/TTL, mencionar `data/cache/` na estrutura
- [x] 3.3 Atualizar `AGENTS.md`: linha da arquitetura sobre CLI ("command `run`") → comandos `extract` e `run` + nota do cache
- [x] 3.4 Gate final: `uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest`
