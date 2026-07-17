## Context

Pipeline ETL didática que integra dados de duas APIs públicas para gerar estatísticas sobre universidades por país e continente. O projeto tem maturidade alvo 2.5/5: organizado e extensível, porém sem complexidade enterprise. Ambiente Python 3.12+ gerenciado por `uv`.

## Goals / Non-Goals

**Goals:**
- Pipeline funcional pura: `extract → transform → aggregate → load`
- Resiliente a falhas de rede (retry, timeout, cache offline)
- Join correto com normalização de aliases de nome de país
- Persistência de dados crus e resultados em Parquet/CSV
- CLI minimalista para execução do pipeline

**Non-Goals:**
- Orquestração complexa (sem DAGs, sem scheduler)
- Processamento incremental ou CDC
- Interface web ou API REST
- Containerização ou deploy automatizado
- Suporte a múltiplos formatos de saída além de CSV e Parquet

## Decisions

### 1. Polars como engine único de transformação

**Alternativa considerada:** Dicionários/listas nativos + Pandas.

**Decisão:** Polars. Lazy evaluation reduz memória, API funcional alinha com o design, e `scan_parquet` permite pipeline inteiro lazy até o `collect()` final. Evita overhead de converter entre tipos intermediários.

### 2. Pydantic apenas na borda (extract)

**Alternativa considerada:** Pydantic em todas as camadas.

**Decisão:** Modelos Pydantic validam e aplainam JSON apenas no momento do extract. Após isso, o pipeline trabalha com Polars DataFrames. Isso evita validação redundante e maximiza performance onde a validação já foi feita.

### 3. Cache offline em Parquet

**Alternativa considerada:** Cache em JSON cru, ou sempre bater na API.

**Decisão:** Após parse e validação Pydantic, salvar DataFrames crus em `data/raw/<source>.parquet`. Se o arquivo existe, pula API. Isso resolve dois problemas: desenvolvimento offline e evitar sobrecarregar APIs públicas com repetição.

### 4. Mapa de aliases estático para normalização de nomes de países

**Alternativa considerada:** Fuzzy matching com `difflib`/`fuzzywuzzy`.

**Decisão:** Mapa estático em `src/transform/aliases.py` com entradas conhecidas (ex: `"United States" → "United States of America"`). Mais simples, previsível e sem dependências extras. Se novos aliases surgirem, basta adicionar ao dicionário.

### 5. Funções puras e composition root

**Alternativa considerada:** Classes com estado (ETLProcessor, Extractor, etc).

**Decisão:** Cada etapa é uma função pura `(DataFrame) → DataFrame`. A orquestração no `pipeline/run.py` compõe essas funções. Elimina estado compartilhado, facilita testes unitários sem mocking e torna o fluxo de dados explícito.

### 6. Typer CLI com commands separados

**Alternativa considerada:** `if __name__ == "__main__"` direto.

**Decisão:** Typer provê CLI tipada com `run` e `clear-cache`. Sem boilerplate de argparse, ajuda inline automática. O módulo `main.py` serve como entry point.

### 7. Estrutura de diretórios por responsabilidade

```
src/
├── extract/       # fetch_countries(), fetch_universities()
│   └── fetcher.py
├── transform/     # normalize(), join_data(), enrich(), aggregate()
│   ├── normalize.py
│   ├── join_data.py
│   ├── enrich.py
│   ├── aggregate.py
│   └── aliases.py
├── load/          # to_csv(), to_parquet()
│   └── loader.py
├── pipeline/      # run() — composition root
│   └── run.py
├── models/        # Pydantic CountryModel, UniversityModel
│   ├── country.py
│   └── university.py
└── utils/         # httpx client factory, logging
    ├── http.py
    └── log.py
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Universities API pode mudar schema | Pydantic valida na borda; campos extras são ignorados com `Extra.ignore` |
| REST Countries pode adicionar/renomear campos | Idem |
| Alias map não cobre todos os casos | Log de warning com países não matchados permite identificar e adicionar novos aliases |
| Cache pode ficar stale | CLI `clear-cache` permite reset manual |
| Polars não é tão difundido quanto Pandas | Projeto é didático; Polars é stack moderna e alvo de aprendizado |
| httpx async simplificado para sync | Para POC, usar `httpx.Client` síncrono com timeout; async seria over-engineer |