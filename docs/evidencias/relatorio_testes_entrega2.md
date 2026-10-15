# Relatório de Execução dos Testes Automatizados — Entrega 2

**Data:** 14/10/2026  
**Commit avaliado:** `7dbda30` (`7dbda300e21d770e9c141381278b1c7f0ea6d1cd`)  
**Escopo:** evidências coletadas nesta execução, sem alterações em `analyzer/`, testes, configuração de testes, Docker ou CI.  
**Atualização em 15/10/2026:** execução Docker local incluída (#118), no commit `49696c0` da `develop`, cuja árvore é idêntica à da `main` em `93e0fcb` (tag `v2.0.0`). Entre `7dbda30` e `49696c0` só entraram documentos; `analyzer/` e `tests/` não mudaram.

## a) Resumo das execuções

| Ambiente | Resultado | Total | Passaram | Falharam | Tempo |
|---|---|---:|---:|---:|---:|
| Local — Windows, Python 3.11.9, pytest 9.1.1, `.venv` | **PASSOU** (`./scripts/run_harness.sh`) | 246 | 246 | 0 | 3,05 s |
| Docker local — Docker 29.8.0, Compose v5.5.1, Python 3.11.17 no contêiner (`docker compose run --rm test`), commit `49696c0` | **PASSOU** | 246 | 246 | 0 | 10,16 s |
| CI — Ubuntu, Python 3.11.17, job pytest | **PASSOU** | 246 | 246 | 0 | 0,57 s |
| CI — Ubuntu, job Docker | **PASSOU** | 246 | 246 | 0 | 0,78 s |

Na coleta de 14/10, o Docker local não chegou a iniciar a suíte: `docker compose run --rm test` terminou com código 1 porque o daemon do Docker Desktop estava desligado. A execução foi refeita em 15/10, com o Docker Desktop ativo, e terminou com código 0. Uma execução anterior no commit `6f9a079` também passou (246 em 7,20 s) e está registrada no [PR #121](https://github.com/mariisena/phishguard-bootcamp-iii/pull/121).

### Execuções locais consecutivas — RNF-02

Além das execuções repetidas, a suíte completa foi executada pelo harness quatro vezes no total. Todos os logs registram 246 testes aprovados. As execuções 2 e 3 foram duas execuções completas consecutivas, sem outra execução de teste entre elas, e têm resultados iguais:

| Execução | Resultado | Total | Passaram | Falharam | Tempo | Log |
|---|---|---:|---:|---:|---:|---|
| Execução 1 | PASSOU | 246 | 246 | 0 | 3,28 s | [`harness_20261014_085224.log`](../../logs/harness_20261014_085224.log) |
| Execução 2 | PASSOU | 246 | 246 | 0 | 4,17 s | [`harness_20261014_090602.log`](../../logs/harness_20261014_090602.log) |
| Execução 3 | PASSOU | 246 | 246 | 0 | 3,77 s | [`harness_20261014_090621.log`](../../logs/harness_20261014_090621.log) |
| Execução 4 — comando exato `./scripts/run_harness.sh` | PASSOU | 246 | 246 | 0 | 3,05 s | [`harness_20261014_091204.log`](../../logs/harness_20261014_091204.log) |

`RNF-02` — determinismo — também é exercitado por testes próprios; a repetição da suíte confirma que os totais e resultados destas execuções permaneceram iguais. Os logs completos ficam em `logs/`, pasta ignorada pelo Git.

### CI e artefato

- Execução mais recente na `develop`, branch congelada para esta entrega, no mesmo commit: [workflow run 38551248488](https://github.com/mariisena/phishguard-bootcamp-iii/actions/runs/38551248488).
- Resultado geral: **success**. Os jobs `Test Harness (pytest)` e `Test Harness (Docker)` concluíram com sucesso.
- Artefato publicado: [`evidencias-test-harness` (ID 11887315105)](https://github.com/mariisena/phishguard-bootcamp-iii/actions/runs/38551248488/artifacts/11887315105).
- O artefato foi localizado pela API do GitHub Actions. A tentativa de baixar o ZIP para este ambiente não concluiu; os trechos abaixo foram obtidos diretamente dos logs dos jobs pela API. A CLI `gh` não está instalada neste ambiente, então `gh run list`/`gh run view` não puderam ser executados; a execução equivalente foi consultada pelo GitHub Actions.

## b) Arquivos de teste e requisitos cobertos

Lista obtida da árvore real `tests/`, equivalente a `find tests -name "test_*.py"`:

| Arquivo de teste | Requisitos do SDD cobertos |
|---|---|
| [`test_api.py`](../../tests/integration/test_api.py) | RF-01, RF-16, RF-17; RNF-02, RNF-09; contratos HTTP dos §§5.2–5.3 |
| [`test_detector.py`](../../tests/integration/test_detector.py) | RF-01–RF-03, RF-15; RN-02–RN-04; cenários integrados seguro, suspeito e perigoso |
| [`test_performance.py`](../../tests/integration/test_performance.py) | RNF-01 |
| [`test_at_symbol.py`](../../tests/unit/test_at_symbol.py) | RF-06, RN-07 |
| [`test_blocklist.py`](../../tests/unit/test_blocklist.py) | RF-15, RN-03, RN-04, N-07 |
| [`test_brand_impersonation.py`](../../tests/unit/test_brand_impersonation.py) | RF-10, RN-05, RN-07 |
| [`test_config_consistency.py`](../../tests/unit/test_config_consistency.py) | **A DEFINIR** — verifica consistência entre listas do SDD e `config.py`, sem RF/RN/RNF identificado no arquivo |
| [`test_excessive_subdomains.py`](../../tests/unit/test_excessive_subdomains.py) | RF-07 |
| [`test_ip_domain.py`](../../tests/unit/test_ip_domain.py) | RF-05 |
| [`test_missing_https.py`](../../tests/unit/test_missing_https.py) | RF-12 |
| [`test_punycode_homograph.py`](../../tests/unit/test_punycode_homograph.py) | RF-11, RNF-07 |
| [`test_scorer.py`](../../tests/unit/test_scorer.py) | RF-17; RN-01–RN-07; RNF-02 |
| [`test_suspicious_keywords.py`](../../tests/unit/test_suspicious_keywords.py) | RF-14, RN-06 |
| [`test_suspicious_tld.py`](../../tests/unit/test_suspicious_tld.py) | RF-08 |
| [`test_url_length.py`](../../tests/unit/test_url_length.py) | RF-13, N-01 |
| [`test_url_normalizer.py`](../../tests/unit/test_url_normalizer.py) | RF-04, RF-05, RF-17; N-01–N-09; RNF-07 |
| [`test_url_shortener.py`](../../tests/unit/test_url_shortener.py) | RF-09, RN-08 |

## c) Rastreabilidade dos casos de borda do §7

Cada caso de borda listado no §7 do SDD tem pelo menos um teste correspondente. **Casos sem cobertura: nenhum.**

| Caso de borda do §7 | Teste que cobre o caso |
|---|---|
| URL vazia, `None` ou tipo incorreto | `tests/unit/test_url_normalizer.py::test_n02_entrada_vazia_e_invalida`; `tests/unit/test_url_normalizer.py::test_n01_entrada_nao_string_e_invalida` |
| URL sem esquema (`www.exemplo.com`) | `tests/unit/test_url_normalizer.py::test_n03_url_sem_esquema_e_invalida` |
| Host IPv4 e IPv6 | `tests/unit/test_ip_domain.py::test_host_ipv4_dispara`; `tests/unit/test_ip_domain.py::test_host_ipv6_dispara` |
| URL com `@` na autoridade/userinfo | `tests/unit/test_at_symbol.py::test_multiplos_arrobas_disparam_uma_unica_vez` |
| Domínio Punycode | `tests/unit/test_punycode_homograph.py::test_host_ja_em_punycode_dispara` |
| Domínio com homoglifo Unicode | `tests/unit/test_punycode_homograph.py::test_host_com_homoglifo_unicode_dispara` |
| URL de encurtador conhecido | `tests/unit/test_url_shortener.py::test_encurtadores_da_lista_normativa_disparam[bit.ly]` |
| URL com mais de 2048 caracteres | `tests/unit/test_url_normalizer.py::test_n02_entrada_acima_do_limite_e_invalida` |
| Domínio com muitos subdomínios | `tests/unit/test_excessive_subdomains.py::test_muitos_subdominios_dispara` |
| Domínio oficial de marca monitorada não dispara impersonação | `tests/unit/test_brand_impersonation.py::test_dominio_oficial_nao_dispara` |
| Palavra sensível sem outro sinal não eleva a classificação | `tests/unit/test_scorer.py::test_rn06_palavra_chave_isolada_nao_pontua` |
| Mesma URL duas vezes produz resultado idêntico | `tests/unit/test_scorer.py::test_rnf02_resultado_deterministico`; também `tests/integration/test_api.py::TestAnalyzeSuccess::test_same_request_returns_identical_body` |

## d) Evidência do RNF-01 — desempenho

Executado isoladamente em `tests/integration/test_performance.py`:

```text
tests/integration/test_performance.py::test_performance_rnf01_analysis_under_300ms PASSED [100%]
============================== 1 passed in 0.24s ==============================
```

Resultado: **1 passou, 0 falharam**, em 0,24 s para a execução do teste. O limite do SDD para RNF-01 é **até 300 ms por análise**; o teste verifica que a média de análise por URL é inferior a 300 ms. A saída de pytest não imprime o valor dessa média, então nenhum valor de média é afirmado neste relatório.

## e) Evidência do RNF-02 — determinismo

As execuções consecutivas 2 e 3 foram comparadas: ambas coletaram 246 testes e terminaram com `246 passed`, sem falhas. Tempos registrados individualmente: 4,17 s e 3,77 s. A execução 4, posterior, também passou com 246 testes. A suíte contém ainda `test_rnf02_resultado_deterministico`, que compara o resultado da mesma entrada.

## f) Trechos finais dos logs

### Local — execução principal

Fonte: [`harness_20261014_091204.log`](../../logs/harness_20261014_091204.log).

```text
tests/unit/test_url_shortener.py::test_encurtador_no_meio_do_host_nao_dispara PASSED [100%]

============================= 246 passed in 3.05s =============================
```

### Docker local — `docker compose run --rm test` (15/10, commit `49696c0`)

Início e final da saída do contêiner:

```text
platform linux -- Python 3.11.17, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python
rootdir: /app
collecting ... collected 246 items
...
tests/unit/test_url_shortener.py::test_www_bit_ly_dispara PASSED         [ 99%]
tests/unit/test_url_shortener.py::test_notbit_ly_nao_dispara PASSED      [ 99%]
tests/unit/test_url_shortener.py::test_encurtador_no_meio_do_host_nao_dispara PASSED [100%]

============================= 246 passed in 10.16s =============================
```

O comando usa `--rm`, então o contêiner é removido ao final.

### CI — job `Test Harness (pytest)`

Fonte: log do job associado ao [workflow run 38551248488](https://github.com/mariisena/phishguard-bootcamp-iii/actions/runs/38551248488).

```text
tests/unit/test_url_shortener.py::test_encurtador_no_meio_do_host_nao_dispara PASSED [100%]
============================= 246 passed in 0.57s ==============================
```

### CI — job `Test Harness (Docker)`

O job Docker do mesmo workflow também executou a suíte em container:

```text
tests/unit/test_url_shortener.py::test_encurtador_no_meio_do_host_nao_dispara PASSED [100%]
============================= 246 passed in 0.78s ==============================
```

## g) Evolução do número de testes

`152` (valor informado para a Entrega 1, **não confirmado** pelo `git log` nem por PR consultável) → `189` (registrado nos PRs [#85](https://github.com/mariisena/phishguard-bootcamp-iii/pull/85) e [#86](https://github.com/mariisena/phishguard-bootcamp-iii/pull/86)) → `241` (registrado no PR [#115](https://github.com/mariisena/phishguard-bootcamp-iii/pull/115)) → **246** (total real coletado nesta execução).

## h) Consistência dos resultados

- A suíte local principal e ambas as repetições coletaram 246 testes; em cada uma, 246 passaram e 0 falharam.
- Os jobs CI pytest e Docker também registram 246 passaram e 0 falharam.
- A execução Docker local de 15/10 coletou 246 testes; 246 passaram e 0 falharam.
- Para cada execução concluída, `passaram + falharam = total` (`246 + 0 = 246`).
- Os três ambientes exigidos (local, Docker e CI) têm 100% de aprovação.
- Não foram identificados casos de borda do §7 sem teste correspondente.
- O total `152` da evolução histórica não foi confirmado e permanece assinalado como não verificado.
