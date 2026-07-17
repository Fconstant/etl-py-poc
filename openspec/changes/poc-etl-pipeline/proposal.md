## Why

Demonstrar a construção de uma pipeline ETL moderna, resiliente e didática em Python 3.12+ com maturidade 2.5/5, aplicando programação funcional pura e mitigando problemas comuns de produção como falhas de rede de APIs instáveis, dessincronização de joins de nomes de países, e processamento ineficiente de JSONs complexos e aninhados.

## What Changes

- Criação de um pipeline ETL completo que consome dados das APIs REST Countries e Universities.
- Implementação de um mecanismo de cache local em disco (Parquet) para desenvolvimento rápido offline.
- Resolução de inconsistências de nomes de países (aliases) no join para evitar perda de dados.
- Mapeamento e validação de dados aninhados das APIs usando Pydantic na borda do sistema.
- Processamento e transformações eficientes usando Polars Lazy DataFrame.
- Interface de linha de comando CLI minimalista via Typer.

## Capabilities

### New Capabilities
- `etl-extract`: Downloads data from REST Countries and Universities APIs, parses them using flat Pydantic models, and writes raw data locally as Parquet cache.
- `etl-transform`: Normalizes country names using static alias resolution, performs a clean join, and enriches university data with country attributes (ISO code, continent, population, currency).
- `etl-aggregate-load`: Generates business statistics (universities per country, universities per continent, top 10 countries) and writes results to clean CSV and Parquet files, orchestrated by a simple CLI.

### Modified Capabilities
<!-- None -->

## Impact

- Novas dependências adicionadas ao projeto (`polars`, `pydantic`, `httpx`, `typer`).
- Estruturação de diretórios limpa sob `src/` (`extract`, `transform`, `load`, `pipeline`, `models`, `utils`).
- Configuração do ambiente via `uv`.
