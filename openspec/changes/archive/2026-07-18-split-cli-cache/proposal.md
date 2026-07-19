# Proposal: split-cli-cache

## Why

Hoje o CLI expõe um único comando que sempre bate nas duas APIs externas a cada execução, mesmo quando os dados brutos não mudaram. Isso torna iterações de desenvolvimento lentas e frágeis (dependência de rede a cada run). Separar extração de execução e adicionar cache local com TTL elimina chamadas redundantes.

## What Changes

- **BREAKING**: comando único `start` (`uv run etl`) deixa de existir; CLI passa a ter dois subcomandos explícitos: `etl extract` e `etl run`.
- Novo comando `etl extract`: busca dados das duas APIs (REST Countries + Universities) e grava cache local em `data/cache/`.
- Novo comando `etl run`: executa o pipeline completo usando cache local se existente e dentro do TTL (1 dia); caso contrário, extrai das APIs e **também atualiza o cache** antes de prosseguir.
- Cache com TTL de 1 dia: timestamp de gravação persistido para invalidação futura.
- `data/cache/` adicionado ao `.gitignore`.
- Documentação atualizada: README (seção Uso, estrutura) e AGENTS.md (linha sobre CLI).

## Capabilities

### New Capabilities

- `etl-cli`: interface de linha de comando do pipeline — subcomandos `extract` (extrai e cacheia) e `run` (pipeline completo, cache-first).

### Modified Capabilities

- `etl-extract`: adiciona requisitos de cache local — leitura cache-first com TTL de 1 dia e escrita (write-through) do cache após extração das APIs.

## Impact

- `src/cli.py`: comando `start` substituído por `extract` e `run`.
- `src/extract/`: novo módulo de cache (save/load com TTL); funções de obtenção de dados passam a consultar cache antes das APIs.
- `src/pipeline/run.py`: passa a usar as funções cache-aware.
- `data/cache/`: novo diretório de artefatos locais (gitignored).
- `README.md` e `AGENTS.md`: docs de uso do CLI atualizadas.
- Sem novas dependências — stdlib + polars já cobrem persistência e timestamp.
