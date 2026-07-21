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
uv run etl extract        # fetch APIs and write local cache to data/cache/
uv run etl run            # full pipeline (uses cache if valid, otherwise fetches and updates cache)
uv run etl run --export-bigquery   # full pipeline + upload 4 tables to BigQuery (best-effort)
uv run etl export-bq      # upload existing data/output/*.parquet to BigQuery (hard-fail)
uv run etl view           # generate HTML report from cached output CSVs
```

Local cache has a 1-day TTL (invalidated by file modification time). `etl extract` always hits the APIs and overwrites the cache; `etl run` only hits the APIs when the cache is missing or expired — and also updates the cache in that case.

`etl run` is local-only by default. BigQuery upload requires `--export-bigquery` (also aliased `--export-bq`); failures are logged as warnings but do not stop the pipeline. `etl export-bq` reads the 4 Parquet files from `data/output/` and uploads them to BigQuery — it fails with a non-zero exit code if any file is missing or any write fails.

Outputs in `data/output/`:

- `universities.csv` / `.parquet` (enriched raw data)
- `universities_per_country.csv` / `.parquet`
- `universities_per_continent.csv` / `.parquet`
- `top10_universities.csv` / `.parquet`
- `report.html`

### BigQuery setup (optional)

BigQuery output is opt-in. To enable it:

1. Create or use an existing GCP project with the BigQuery API enabled.
2. Create a service account with the `roles/bigquery.dataEditor` and `roles/bigquery.jobUser` roles, and download a JSON key.
3. Authenticate via Application Default Credentials by setting `GOOGLE_APPLICATION_CREDENTIALS` to the key file path (or run `gcloud auth application-default login` for personal credentials).
4. Set the project and dataset via environment variables (a `.env` file works — `python-dotenv` is loaded before config reads):
   ```sh
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_BIGQUERY_DATASET="etl_universities"   # optional, this is the default
   ```
5. Run `uv run etl run --export-bigquery` (during the pipeline) or `uv run etl export-bq` (from existing Parquet files).

The dataset and the 4 tables (`universities`, `universities_per_country`, `universities_per_continent`, `top10_universities`) are created automatically on first write with `WRITE_TRUNCATE` disposition — re-running overwrites the data. No partitioning or clustering is applied (see ADR-002).

### Testing

```sh
uv run pytest            # run all tests
uv run pytest tests/test_normalize.py   # run a single test file
uv run pytest -k "test_name"            # run tests matching a pattern
```

### Structure

```
src/
├── extract/       # fetch_countries, fetch_universities (httpx + pydantic), cache (data/cache, 1-day TTL)
├── transform/     # normalize, join, enrich, aggregate (polars, difflib)
├── load/          # to_csv, to_parquet, to_bigquery (opt-in), BigQuery config
├── pipeline/      # run() — stage composition; export_bq — upload from local files
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
uv run etl extract        # extrai das APIs e grava cache local em data/cache/
uv run etl run            # pipeline completo (usa cache se válido, senão extrai e atualiza cache)
uv run etl run --export-bigquery   # pipeline completo + sobe 4 tabelas ao BigQuery (best-effort)
uv run etl export-bq      # sobe data/output/*.parquet ao BigQuery (hard-fail)
uv run etl view           # gera relatório HTML a partir dos CSVs de saída
```

O cache local tem TTL de 1 dia (invalidado pela data de gravação do arquivo). `etl extract` sempre bate nas APIs e sobrescreve o cache; `etl run` só bate nas APIs se o cache estiver ausente ou expirado — e nesse caso também atualiza o cache.

`etl run` é só local por padrão. O upload ao BigQuery requer `--export-bigquery` (alias `--export-bq`); falhas são logadas como warnings mas não interrompem o pipeline. `etl export-bq` lê os 4 arquivos Parquet de `data/output/` e sobe ao BigQuery — falha com código de saída não-zero se algum arquivo estiver ausente ou alguma escrita falhar.

Resultados em `data/output/`:

- `universities.csv` / `.parquet` (dados enriquecidos brutos)
- `universities_per_country.csv` / `.parquet`
- `universities_per_continent.csv` / `.parquet`
- `top10_universities.csv` / `.parquet`
- `report.html`

### Setup BigQuery (opcional)

A saída para BigQuery é opt-in. Para habilitar:

1. Crie ou use um projeto GCP com a BigQuery API habilitada.
2. Crie uma service account com os papéis `roles/bigquery.dataEditor` e `roles/bigquery.jobUser`, e baixe a chave JSON.
3. Autentique via Application Default Credentials apontando `GOOGLE_APPLICATION_CREDENTIALS` para o arquivo de chave (ou rode `gcloud auth application-default login` para credenciais pessoais).
4. Defina o projeto e o dataset via variáveis de ambiente (arquivo `.env` funciona — `python-dotenv` é carregado antes da leitura de config):
   ```sh
   export GOOGLE_CLOUD_PROJECT="seu-project-id"
   export GOOGLE_BIGQUERY_DATASET="etl_universities"   # opcional, este é o default
   ```
5. Rode `uv run etl run --export-bigquery` (durante o pipeline) ou `uv run etl export-bq` (a partir dos Parquet existentes).

O dataset e as 4 tabelas (`universities`, `universities_per_country`, `universities_per_continent`, `top10_universities`) são criados automaticamente na primeira escrita com disposition `WRITE_TRUNCATE` — re-rodar sobrescreve os dados. Sem particionamento ou clustering (ver ADR-002).

### Testes

```sh
uv run pytest            # roda todos os testes
uv run pytest tests/test_normalize.py   # roda um arquivo de teste
uv run pytest -k "test_name"            # roda testes que combinam com o padrão
```

### Estrutura

```
src/
├── extract/       # fetch_countries, fetch_universities (httpx + pydantic), cache (data/cache, TTL 1 dia)
├── transform/     # normalize, join, enrich, aggregate (polars, difflib)
├── load/          # to_csv, to_parquet, to_bigquery (opt-in), config BigQuery
├── pipeline/      # run() — composição das etapas; export_bq — upload a partir de arquivos locais
├── models/        # pydantic schemas (Country, University)
└── utils/         # log, http client
```
