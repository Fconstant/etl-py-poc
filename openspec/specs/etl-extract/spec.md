# etl-extract Specification

## Purpose
TBD - created by archiving change poc-etl-pipeline. Update Purpose after archive.
## Requirements
### Requirement: Fetch countries from REST Countries API
The system SHALL fetch country data from `https://restcountries.com/v3.1/all` using httpx with a default timeout of 10 seconds and up to 3 retries on transient errors.

#### Scenario: Successful fetch
- **WHEN** the API responds with HTTP 200
- **THEN** raw JSON is returned as a list of country dicts

#### Scenario: API timeout
- **WHEN** the API does not respond within 10 seconds
- **THEN** the system retries up to 3 times with exponential backoff before raising a `RuntimeError`

#### Scenario: API returns 5xx
- **WHEN** the API returns HTTP 500, 502, or 503
- **THEN** the system retries up to 3 times before raising a `RuntimeError`

#### Scenario: API returns 4xx
- **WHEN** the API returns HTTP 404 or 429
- **THEN** the system raises an error immediately without retrying

### Requirement: Fetch universities from Universities API
The system SHALL fetch university data from `http://universities.hipolabs.com/search` using httpx with the same timeout and retry strategy.

#### Scenario: Successful fetch
- **WHEN** the API responds with HTTP 200
- **THEN** raw JSON is returned as a list of university dicts

#### Scenario: Connection refused
- **WHEN** the API host is unreachable
- **THEN** the system logs a warning and raises a `RuntimeError`

### Requirement: Parse raw JSON into flat typed models
The system SHALL validate and flatten nested JSON from both APIs using Pydantic `BaseModel` classes defined in `src/models/`.

#### Scenario: Countries JSON parsed
- **WHEN** raw country JSON is received
- **THEN** each country is validated and flattened into a model with fields: `name`, `iso_code`, `continent`, `population`, `currency_name`

#### Scenario: Universities JSON parsed
- **WHEN** raw university JSON is received
- **THEN** each university is validated and flattened into a model with fields: `name`, `country`, `state_province`, `domains`, `web_pages`

#### Scenario: Invalid JSON rejected
- **WHEN** a country entry is missing the required `name` field
- **THEN** Pydantic raises `ValidationError` and the entry is skipped with a warning logged

### Requirement: Cache local de dados extraídos com TTL de 1 dia

O sistema SHALL persistir os DataFrames validados de cada fonte como Parquet em `data/cache/` (`countries.parquet`, `universities.parquet`), usando o timestamp de gravação do arquivo (mtime) para invalidação com TTL de 86400 segundos (1 dia).

#### Scenario: Gravação do cache após extração
- **WHEN** dados de uma fonte são extraídos e validados com sucesso
- **THEN** o DataFrame é gravado como Parquet em `data/cache/<fonte>.parquet`, registrando o momento da gravação

#### Scenario: DataFrame vazio não é cacheado
- **WHEN** a extração resulta em DataFrame vazio
- **THEN** o sistema não grava cache para essa fonte

### Requirement: Leitura cache-first com fallback para API

O sistema SHALL, ao obter dados de uma fonte, retornar o cache local se existente e dentro do TTL; caso contrário SHALL extrair da API e atualizar o cache antes de retornar (write-through).

#### Scenario: Cache hit
- **WHEN** `data/cache/<fonte>.parquet` existe com idade menor que 86400 segundos
- **THEN** o DataFrame é carregado do arquivo, sem chamada à API

#### Scenario: Cache miss por ausência
- **WHEN** `data/cache/<fonte>.parquet` não existe
- **THEN** o sistema extrai da API, grava o cache e retorna os dados

#### Scenario: Cache miss por expiração
- **WHEN** `data/cache/<fonte>.parquet` tem idade maior ou igual a 86400 segundos
- **THEN** o sistema extrai da API, sobrescreve o cache e retorna os dados

#### Scenario: Cache corrompido tratado como miss
- **WHEN** a leitura do Parquet de cache falha
- **THEN** o sistema trata como cache-miss e segue para a extração via API

#### Scenario: Validade independente por fonte
- **WHEN** o cache de uma fonte está válido e o de outra está expirado
- **THEN** apenas a fonte expirada é re-extraída da API

