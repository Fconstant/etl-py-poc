# ETL Pipeline — POC didática

[🇺🇸 English](#english) · [🇧🇷 Português](#português)

---

## English

Didactic ETL pipeline that cross-references data from [REST Countries](https://restcountries.com/) and [Universities](https://universities.hipolabs.com/) APIs to generate university statistics by country and continent.

### Stack

- **uv** — dependency and environment management
- **httpx** — HTTP requests with retry and timeout
- **polars** — data transformation engine
- **pydantic** — JSON validation and flattening at the boundary
- **typer** — CLI

### Setup

```sh
uv sync
```

### Usage

```sh
uv run etl extract   # fetch APIs and write local cache to data/cache/
uv run etl run       # full pipeline (uses cache if valid, otherwise fetches and updates cache)
```

Local cache has a 1-day TTL (invalidated by file modification time). `etl extract` always hits the APIs and overwrites the cache; `etl run` only hits the APIs when the cache is missing or expired — and also updates the cache in that case.

Outputs in `data/output/`:
- `universities_per_country.csv` / `.parquet`
- `universities_per_continent.csv` / `.parquet`
- `top10_universities.csv` / `.parquet`

### Structure

```
src/
├── extract/       # fetch_countries, fetch_universities (httpx + pydantic), cache (data/cache, 1-day TTL)
├── transform/     # normalize, join, enrich, aggregate (polars, difflib)
├── load/          # to_csv, to_parquet
├── pipeline/      # run() — stage composition
├── models/        # pydantic schemas (Country, University)
└── utils/         # log, http client
```

---

## Português

Pipeline ETL em Python 3.12+ que cruza dados das APIs [REST Countries](https://restcountries.com/) e [Universities](http://universities.hipolabs.com/) para gerar estatísticas de universidades por país e continente.

### Stack

- **uv** — gerenciamento de dependências e ambiente
- **httpx** — requisições HTTP com retry e timeout
- **polars** — engine de transformação de dados
- **pydantic** — validação e flatten de JSON na borda
- **typer** — CLI

### Setup

```sh
uv sync
```

### Uso

```sh
uv run etl extract   # extrai das APIs e grava cache local em data/cache/
uv run etl run       # pipeline completo (usa cache se válido, senão extrai e atualiza cache)
```

O cache local tem TTL de 1 dia (invalidado pela data de gravação do arquivo). `etl extract` sempre bate nas APIs e sobrescreve o cache; `etl run` só bate nas APIs se o cache estiver ausente ou expirado — e nesse caso também atualiza o cache.

Resultados em `data/output/`:
- `universities_per_country.csv` / `.parquet`
- `universities_per_continent.csv` / `.parquet`
- `top10_universities.csv` / `.parquet`

### Estrutura

```
src/
├── extract/       # fetch_countries, fetch_universities (httpx + pydantic), cache (data/cache, TTL 1 dia)
├── transform/     # normalize, join, enrich, aggregate (polars, difflib)
├── load/          # to_csv, to_parquet
├── pipeline/      # run() — composição das etapas
├── models/        # pydantic schemas (Country, University)
└── utils/         # log, http client
```
