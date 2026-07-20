# Proposal: fix-country-name-aliases

## Why

O log do pipeline mostra 19 países não casados na normalização (`Unmatched countries: {'Russian Federation', 'Korea, Republic of', ...}`). A causa não é ajuste de threshold: a Universities API usa nomes formais ISO 3166 com inversão por vírgula ("Korea, Republic of"), enquanto o REST Countries fornece nomes comuns ("South Korea"). Os ratios do `difflib` para esses pares ficam entre 0.3–0.6 — nenhum cutoff sensato os aproxima, e baixar o cutoff geraria falsos positivos (ex.: Niger/Nigeria) antes de resolver qualquer um deles. Consequência atual: todas as universidades desses países (Rússia, as duas Coreias, Taiwan, Venezuela, etc.) são silenciosamente descartadas do join.

## What Changes

- Adicionar arquivo de aliases editável `data/country_aliases.json` (19 entradas), mapeando nomes formais da Universities API para nomes comuns do REST Countries (ex.: `"Russian Federation" -> "Russia"`, `"Swaziland" -> "Eswatini"`). Editável por humanos sem tocar código.
- Exceção no `.gitignore` (`!data/country_aliases.json`) para versionar o arquivo apesar de `data/` ser ignorado.
- Carregamento do JSON encapsulado em `src/transform/normalize.py`: `normalize_universities` carrega `data/country_aliases.json` por padrão; parâmetro opcional `aliases` permite injeção em testes. `run.py` não conhece o arquivo.
- Nova ordem de resolução: match exato → alias → fuzzy (`difflib`, cutoff 0.8 mantido como fallback para variações menores).
- Warning de não casados permanece como rede de segurança para drift futuro das APIs.
- **Aproximação deliberada**: "Congo, the Democratic Republic of the" é mapeado para "Congo" (ISO CG) — o dataset de países não tem a RDC (CD); manter as universidades com atributos aproximados foi preferido a descartá-las. Reavaliar se a fonte incluir a RDC.

## Capabilities

### Modified Capabilities

- `etl-transform`: requisito de normalização de nomes passa de "fuzzy matching apenas" para "exato → alias → fuzzy", com tabela de aliases externa em JSON.

## Impact

- `data/country_aliases.json`: novo arquivo versionado com a tabela de aliases.
- `.gitignore`: exceção `!data/country_aliases.json`.
- `src/transform/normalize.py`: helper `load_country_aliases()` + lookup em `_resolve`; `normalize_universities` carrega o JSON por padrão (parâmetro `aliases` opcional para testes).
- `tests/`: casos cobrindo alias hit, fallback fuzzy e não-casado remanescente.
- Sem novas dependências, sem mudança de schema/modelo/cache.

## Out of Scope

- Ausência da República Democrática do Congo no dataset de países (investigação da fonte/extract, não da normalização).
- Captura de `name.official` / `altSpellings` do REST Countries (opção descartada — ver design.md).
