# Design: fix-country-name-aliases

## Contexto

Evidência coletada na investigação (ratios `difflib.SequenceMatcher`):

| Universities API | REST Countries | ratio |
|---|---|---|
| Russian Federation | Russia | 0.50 |
| Korea, Republic of | South Korea | 0.34 |
| Czech Republic | Czechia | 0.57 |
| Swaziland | Eswatini | 0.47 |
| Taiwan, Province of China | Taiwan | 0.39 |
| Turkiye | Turkey | <0.8 |

Fuzzy matching não cobre pares formal↔comum estruturalmente. O conjunto de nomes da Universities API (hipolabs) é estático — os 19 casos são estáveis.

## Decisão

Tabela de aliases em arquivo externo `data/country_aliases.json` (versionado via exceção no `.gitignore`) + ordem de resolução exato → alias → fuzzy.

- **Formato JSON**: `json.load` produz `dict[str, str]` direto — zero parsing, stdlib. CSV exigiria iteração de linhas para montar o dict.
- **Carregamento encapsulado no transform**: `normalize_universities` carrega o JSON por padrão (`aliases=None` → `load_country_aliases()`); a responsabilidade pelos aliases vive inteira em `normalize.py`, e `run.py` não conhece o arquivo. Desvio deliberado da pureza estrita dos transforms: I/O só no caminho default, e testes injetam dicts pelo parâmetro `aliases` sem tocar disco.
- **Arquivo ausente/JSON inválido**: falha rápida (exceção padrão de `open`/`json.load`). O arquivo é versionado no git — ausência indica repo quebrado, não condição a tolerar.

```
run.py:  normalize_universities(df, country_names)      # aliases carregados internamente

normalize_universities(df, country_names, aliases=None):
    aliases is None?                   → load_country_aliases()   # data/country_aliases.json

_resolve(country):
    country in country_names?          → country          (exato)
    country in aliases?                → alias, se o alvo existir no dataset
    difflib cutoff 0.8                 → melhor match     (fallback)
    senão                              → None + warning
```

## Alternativas descartadas

- **Carregar aliases no composition root (`run.py`)**: manteria transforms 100% puros, mas espalha a responsabilidade dos aliases por dois módulos; encapsular em `normalize.py` mantém tudo num lugar só.
- **Dict hardcoded em `normalize.py`**: exigiria mudança de código para cada ajuste da tabela; arquivo externo permite edição humana sem tocar fonte.
- **CSV em vez de JSON**: também stdlib, mas precisa de parsing linha a linha para virar dict; JSON mapeia direto.
- **Capturar `name.official` + `altSpellings` no extract**: exigiria mudança no `CountryModel`, invalidação do cache Parquet e ainda não cobre inversões por vírgula ("Korea, Republic of" ≠ "Republic of Korea" exato). Mais partes móveis para o mesmo resultado.
- **Heurística de inversão de vírgula** ("A, B" → "B A"): segundo mecanismo além do alias, e ainda precisaria de aliases para Swaziland/Eswatini, Taiwan e Côte d'Ivoire. Um mecanismo só (tabela) cobre tudo.
- **Baixar cutoff do fuzzy**: falsos positivos (Niger/Nigeria, Congo/Mongolia) surgem antes de qualquer ganho.

## Tabela de aliases (19 entradas em `data/country_aliases.json`)

| Universities API | Alias |
|---|---|
| Syrian Arab Republic | Syria |
| Taiwan, Province of China | Taiwan |
| Brunei Darussalam | Brunei |
| Russian Federation | Russia |
| Korea, Democratic People's Republic of | North Korea |
| Korea, Republic of | South Korea |
| Czech Republic | Czechia |
| Côte d'Ivoire | Ivory Coast |
| Virgin Islands, British | British Virgin Islands |
| Tanzania, United Republic of | Tanzania |
| Lao People's Democratic Republic | Laos |
| Moldova, Republic of | Moldova |
| Turkiye | Turkey |
| Venezuela, Bolivarian Republic of | Venezuela |
| Holy See (Vatican City State) | Vatican City |
| Bolivia, Plurinational State of | Bolivia |
| Palestine, State of | Palestine |
| Swaziland | Eswatini |
| Congo, the Democratic Republic of the | Congo |

Todos os alvos verificados como presentes em `data/cache/countries.parquet`.

**Aproximação deliberada**: "Congo, the Democratic Republic of the" → "Congo" (ISO CG, República do Congo). O dataset não contém a RDC (CD); a decisão foi manter as universidades da RDC com atributos aproximados de CG em vez de descartá-las. Se a fonte de países passar a incluir a RDC, atualizar o alias para o novo nome.
