# etl-cli Delta Specification

## ADDED Requirements

### Requirement: Flag --export-bigquery no comando run

O comando `run` SHALL executar apenas saída local (CSV/Parquet para todos os 4 DataFrames) por padrão. A flag opcional `--export-bigquery` / `--export-bq` SHALL habilitar a escrita adicional em BigQuery com política best-effort (falhas logadas, pipeline continua).

#### Scenario: Sem flag (comportamento padrão)
- **WHEN** o usuário executa `uv run etl run` sem flags
- **THEN** o pipeline gera apenas arquivos locais em `data/output/` (8 arquivos: 4 CSV + 4 Parquet); nenhuma operação BigQuery é tentada; nenhuma dependência de rede ou GCP é necessária

#### Scenario: Flag --export-bigquery, BigQuery configurado
- **WHEN** o usuário executa `uv run etl run --export-bigquery` com credenciais GCP configuradas
- **THEN** o pipeline gera arquivos locais E escreve em BigQuery (4 tabelas)

#### Scenario: Flag --export-bigquery, BigQuery não configurado
- **WHEN** o usuário executa `uv run etl run --export-bigquery` sem credenciais GCP configuradas
- **THEN** um warning é exibido (config ausente), arquivos locais são gerados, e o pipeline conclui com sucesso

#### Scenario: Flag abreviada --export-bq
- **WHEN** o usuário executa `uv run etl run --export-bq`
- **THEN** o comportamento é idêntico a `--export-bigquery`

### Requirement: Comando `etl export-bq` exporta arquivos locais para BigQuery

O CLI SHALL expor o subcomando `export-bq` que lê os 4 arquivos Parquet de `data/output/` e os carrega nas tabelas BigQuery correspondentes com `WRITE_TRUNCATE`. O comando NÃO re-executa o pipeline; usa apenas os arquivos já gerados. Falhas de leitura de arquivo ou escrita no BigQuery SHALL causar erro fatal com exit code não-zero.

#### Scenario: Exportação bem-sucedida
- **WHEN** o usuário executa `uv run etl export-bq` com credenciais GCP válidas e os 4 arquivos Parquet existentes em `data/output/`
- **THEN** os 4 DataFrames são carregados em BigQuery (`etl_universities.universities`, `etl_universities.universities_per_country`, `etl_universities.universities_per_continent`, `etl_universities.top10_universities`) e uma mensagem de sucesso é exibida

#### Scenario: Arquivo de saída ausente
- **WHEN** o usuário executa `uv run etl export-bq` mas `data/output/universities.parquet` não existe
- **THEN** o comando falha com `FileNotFoundError` e mensagem clara: "Run `etl run` first to generate output files"

#### Scenario: Falha de credenciais BigQuery
- **WHEN** o usuário executa `uv run etl export-bq` com credenciais GCP inválidas
- **THEN** o comando falha com `RuntimeError` incluindo a mensagem de erro do BigQuery

#### Scenario: Re-exportação sem re-executar pipeline
- **WHEN** o usuário executa `uv run etl run` (gera arquivos locais), depois executa `uv run etl export-bq` (envia para BigQuery), depois corrige credenciais e executa `uv run etl export-bq` novamente
- **THEN** apenas a etapa BigQuery é re-executada; o pipeline (extract + transform) não é re-executado

## MODIFIED Requirements

### Requirement: Comando `etl run` executa pipeline completo cache-first

O CLI SHALL expor o subcomando `run` que executa o pipeline completo (extract → transform → load), obtendo dados do cache local quando válido, e das APIs caso contrário. A fase de load escreve todos os 4 DataFrames (enriched raw + 3 agregados) como arquivos locais (CSV/Parquet). A flag `--export-bigquery` / `--export-bq` habilita adicionalmente a escrita em tabelas BigQuery.

#### Scenario: Cache válido é usado
- **WHEN** o usuário executa `uv run etl run` e o cache existe com idade menor que o TTL
- **THEN** o pipeline usa os dados do cache sem chamar as APIs externas e gera as saídas em `data/output/` (8 arquivos locais)

#### Scenario: Cache ausente dispara extração e atualização do cache
- **WHEN** o usuário executa `uv run etl run` sem cache local
- **THEN** o sistema extrai das APIs, grava o cache em `data/cache/` e completa o pipeline (output local)

#### Scenario: Cache expirado dispara extração e atualização do cache
- **WHEN** o usuário executa `uv run etl run` com cache mais antigo que o TTL
- **THEN** o sistema ignora o cache expirado, extrai das APIs, sobrescreve o cache e completa o pipeline
