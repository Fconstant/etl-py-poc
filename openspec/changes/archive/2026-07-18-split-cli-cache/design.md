# Design: split-cli-cache

## Context

CLI atual (`src/cli.py`) tem um comando único `start` que chama `src/pipeline/run.py:run()`, o qual invoca `fetch_countries()` e `fetch_universities()` diretamente contra as APIs a cada execução. Arquitetura do projeto: funções puras por estágio, validação Pydantic só na borda de extração, Polars depois. Sem dependências de cache existentes. Maturidade alvo 2.5/5 — sem complexidade enterprise.

## Goals / Non-Goals

**Goals:**
- Dois subcomandos: `etl extract` (extrai + grava cache) e `etl run` (pipeline cache-first).
- Cache local em `data/cache/` com TTL de 1 dia, com timestamp de gravação persistido.
- `etl run` com cache stale/ausente extrai das APIs e atualiza o cache (write-through).
- Docs (README, AGENTS.md) refletindo o novo CLI.

**Non-Goals:**
- Flag `--no-cache` / `--force-refresh` (adicionar quando houver necessidade real).
- TTL configurável via env/CLI (constante no código basta para POC).
- Cache por-fonte com TTLs distintos, locking, cache distribuído.
- Invalidação parcial (uma fonte fresh, outra stale → trata por arquivo, natural do design).

## Decisions

### D1: Cache como Parquet por fonte, timestamp = mtime do arquivo

`data/cache/countries.parquet` e `data/cache/universities.parquet`. Validade = `time.time() - os.path.getmtime(path) < 86400`.

- **Por quê**: Parquet já é dependência (polars), preserva schema/dtypes do DataFrame validado. mtime é o "timestamp de gravação" nativo do filesystem — stdlib, zero arquivos extras.
- **Alternativas rejeitadas**:
  - JSON bruto + revalidação Pydantic no load — re-executa validação já feita, viola "validação uma vez na borda".
  - Arquivo sidecar `meta.json` com timestamp — segundo arquivo para manter em sincronia; mtime já registra a data de gravação. Se um dia o cache for copiado entre máquinas (perde mtime), aí sim migrar para sidecar.

### D2: Módulo `src/extract/cache.py` com funções puras

```python
CACHE_DIR = "data/cache"
TTL_SECONDS = 86400  # 1 day

def save_cache(df: pl.DataFrame, name: str) -> None
def load_cache(name: str) -> pl.DataFrame | None  # None se ausente ou stale
```

- **Por quê**: cache é preocupação da borda de extração → mora em `src/extract/`. Funções puras seguem a arquitetura (sem classes stateful). Espelha o formato de `src/load/loader.py`.
- **Alternativa rejeitada**: decorator genérico de cache — abstração especulativa para 2 call sites.

### D3: Funções cache-aware `get_countries()` / `get_universities()`

Em `src/extract/cache.py` (ou nos próprios módulos fetch):

```python
def get_countries() -> pl.DataFrame:
    cached = load_cache("countries")
    if cached is not None:
        return cached
    df = fetch_countries()
    save_cache(df, "countries")
    return df
```

`pipeline/run.py` troca `fetch_*()` por `get_*()`. `fetch_*()` permanecem intocadas (só rede+validação).

- **Por quê**: separação limpa — fetch = rede, get = política de cache. Pipeline não conhece cache.

### D4: CLI com dois comandos nomeados

```python
@app.command()
def extract() -> None:  # fetch both + save_cache, sempre bate na API (refresh explícito)

@app.command()
def run() -> None:      # pipeline cache-first
```

Comando `start` removido. Com 2+ comandos o Typer exige subcomando: `uv run etl extract` / `uv run etl run`.

- **Nota**: `etl extract` sempre extrai e sobrescreve o cache (é o gesto explícito de refresh do usuário); não consulta TTL.

### D5: DataFrame vazio não é cacheado

`save_cache` ignora DataFrame vazio (`df.is_empty()`) — evita "envenenar" o cache com resultado de extração falha parcial por 1 dia.

## Risks / Trade-offs

- [mtime perdido em cópia/checkout do cache] → dir é gitignored e local-only; aceitável. Migração p/ sidecar JSON documentada em D1 se necessário.
- [Cache stale de uma fonte, fresh de outra] → cada arquivo valida TTL independente; pior caso: uma chamada de API a mais. OK.
- [Parquet de cache corrompido (escrita interrompida)] → `load_cache` trata exceção de leitura como cache-miss (retorna None) e segue para API.
- [BREAKING: `uv run etl` sem subcomando passa a mostrar help] → docs atualizadas; POC sem consumidores externos.

## Migration Plan

1. Adicionar `src/extract/cache.py` + testes.
2. Trocar comando no CLI, apontar pipeline para `get_*()`.
3. Atualizar `.gitignore`, README, AGENTS.md.
4. Rollback: revert do commit (sem migração de dados — cache é descartável).

## Open Questions

Nenhuma — escopo fechado com o usuário (TTL 1 dia, `data/cache`, comportamento write-through do `run`).
