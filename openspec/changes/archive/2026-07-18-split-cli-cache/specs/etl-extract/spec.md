# Delta: etl-extract

## ADDED Requirements

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
