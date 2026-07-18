# Delta: etl-cli

## ADDED Requirements

### Requirement: Comando `etl extract` extrai e grava cache
O CLI SHALL expor o subcomando `extract` que busca dados das APIs REST Countries e Universities, valida na borda (Pydantic) e grava o resultado como cache local em `data/cache/`, sobrescrevendo cache existente.

#### Scenario: Extração bem-sucedida grava cache
- **WHEN** o usuário executa `uv run etl extract` e as APIs respondem com sucesso
- **THEN** `data/cache/countries.parquet` e `data/cache/universities.parquet` são gravados com os dados validados

#### Scenario: Extract ignora TTL
- **WHEN** o usuário executa `uv run etl extract` com cache ainda válido (dentro do TTL)
- **THEN** o sistema extrai das APIs mesmo assim e sobrescreve o cache (refresh explícito)

### Requirement: Comando `etl run` executa pipeline completo cache-first
O CLI SHALL expor o subcomando `run` que executa o pipeline completo (extract → transform → load), obtendo dados do cache local quando válido, e das APIs caso contrário.

#### Scenario: Cache válido é usado
- **WHEN** o usuário executa `uv run etl run` e o cache existe com idade menor que o TTL
- **THEN** o pipeline usa os dados do cache sem chamar as APIs externas e gera as saídas em `data/output/`

#### Scenario: Cache ausente dispara extração e atualização do cache
- **WHEN** o usuário executa `uv run etl run` sem cache local
- **THEN** o sistema extrai das APIs, grava o cache em `data/cache/` e completa o pipeline

#### Scenario: Cache expirado dispara extração e atualização do cache
- **WHEN** o usuário executa `uv run etl run` com cache mais antigo que o TTL
- **THEN** o sistema ignora o cache expirado, extrai das APIs, sobrescreve o cache e completa o pipeline

### Requirement: Comando único anterior removido
O comando `start` SHALL NOT existir; a invocação passa a exigir subcomando explícito.

#### Scenario: Invocação sem subcomando
- **WHEN** o usuário executa `uv run etl` sem subcomando
- **THEN** o Typer exibe a ajuda listando `extract` e `run`
