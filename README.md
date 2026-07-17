# ETL Pipeline — POC didática

Pipeline ETL em Python 3.12+ que cruza dados das APIs [REST Countries](https://restcountries.com/) e [Universities](http://universities.hipolabs.com/) para gerar estatísticas de universidades por país e continente.

## Stack

- **uv** — gerenciamento de dependências e ambiente
- **httpx** — requisições HTTP com retry e timeout
- **polars** — engine de transformação de dados
- **pydantic** — validação e flatten de JSON na borda
- **typer** — CLI

## Setup

```sh
uv sync
```

## Uso

```sh
uv run etl start
```

Resultados em `data/output/`:
- `universities_per_country.csv` / `.parquet`
- `universities_per_continent.csv` / `.parquet`
- `top10_universities.csv` / `.parquet`

## Estrutura

```
src/
├── extract/       # fetch_countries, fetch_universities (httpx + pydantic)
├── transform/     # normalize, join, enrich, aggregate (polars, difflib)
├── load/          # to_csv, to_parquet
├── pipeline/      # run() — composição das etapas
├── models/        # pydantic schemas (Country, University)
└── utils/         # log, http client
```
