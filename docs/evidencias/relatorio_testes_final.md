# Relatório de Execução dos Testes Aprovados e Cobertura de Código — Etapa Final

**Data da coleta:** 22/10/2026  
**Commit testado:** `794dd4c` (`794dd4c283e3a03d0e4618f7aa6f652a2a522bbe`)  
**Branch local:** `docs/relatorio-testes-final`  
**Escopo:** evidências das execuções local e Docker realizadas neste ambiente e da execução de CI indicada para o mesmo commit.

## 1. Ambiente e comandos executados

### Local

- **Sistema:** Linux `codespaces-3a94b6`, kernel `6.8.0-1064-azure`, arquitetura `x86_64`.
- **Python:** `Python 3.11.17`.
- **pytest:** `pytest 9.1.1`.
- **Comando:** `./scripts/run_harness.sh`, com o ambiente virtual `.venv` ativado.
- **Log:** `logs/harness_20261022_205112.log` (a pasta `logs/` é ignorada pelo Git).

### Docker local

- **Docker:** `Docker version 29.9.2-1, build a82e528901260c8df6073311379eac65f92db204`.
- **Docker Compose:** `Docker Compose version v2.40.3`.
- **Python no contêiner:** `Python 3.11.17`.
- **pytest no contêiner:** `pytest 9.1.1`.
- **Comando executado:** `docker compose run --rm test 2>&1 | tee /tmp/phishguard-final-docker-test-794dd4c.log`.
- **Saída completa:** `/tmp/phishguard-final-docker-test-794dd4c.log` (arquivo temporário, fora do repositório).

### CI

- **Sistema:** `ubuntu-latest` (GitHub Actions).
- **Python:** `3.11.17`.
- **pytest:** `9.1.1`.
- **Comando do job pytest:** `python -m pytest -v --junitxml=test-report.xml --cov-report=xml --cov-report=html | tee logs_test_harness.txt`.
- **Comando do job Docker:** `docker compose run --rm test`.
- **Execução:** [CI run 39851335526](https://github.com/mariisena/phishguard-bootcamp-iii/actions/runs/39851335526).
- **Artefato:** [`evidencias-test-harness` (ID 12456973866)](https://github.com/mariisena/phishguard-bootcamp-iii/actions/runs/39851335526/artifacts/12456973866).

O `gh run view` não pôde ser executado porque a CLI `gh` não está instalada neste ambiente. A execução, os jobs, o SHA e o artefato foram conferidos pelas informações do GitHub Actions; os trechos dos logs CI abaixo foram obtidos dos logs dos respectivos jobs.

## 2. Resumo das execuções

O tempo mostrado é o tempo de execução da suíte reportado pelo pytest, não a duração total de provisionamento do ambiente ou do job CI.

| Ambiente | Resultado | Total | Passaram | Falharam | Tempo |
|---|---|---:|---:|---:|---:|
| Local — `./scripts/run_harness.sh` | **PASSOU** | 251 | 251 | 0 | 2.70 s |
| Docker local — `docker compose run --rm test` | **PASSOU** | 251 | 251 | 0 | 2.81 s |
| CI — job `Test Harness (pytest)` | **PASSOU** | 251 | 251 | 0 | 2.05 s |
| CI — job `Test Harness (Docker)` | **PASSOU** | 251 | 251 | 0 | 1.00 s |

Os dois jobs da CI concluíram com `success`. O SHA da execução é `794dd4c283e3a03d0e4618f7aa6f652a2a522bbe`, o mesmo commit testado localmente e em Docker.

## 3. Cobertura de código

Tabela copiada da saída do pytest local. As execuções Docker local e os dois jobs CI reportaram os mesmos valores por módulo e o mesmo total.

```text
Name                                     Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------------------------
analyzer/__init__.py                         1      0      0      0   100%
analyzer/api.py                             28      0      2      0   100%
analyzer/blocklist.py                       43      0     10      0   100%
analyzer/config.py                          12      0      0      0   100%
analyzer/models.py                          14      0      0      0   100%
analyzer/rules/__init__.py                   0      0      0      0   100%
analyzer/rules/at_symbol.py                  7      0      2      0   100%
analyzer/rules/base.py                      11      0      0      0   100%
analyzer/rules/brand_impersonation.py       16      0      6      0   100%
analyzer/rules/excessive_subdomains.py      10      0      2      0   100%
analyzer/rules/ip_domain.py                  7      0      2      0   100%
analyzer/rules/missing_https.py              7      0      2      0   100%
analyzer/rules/punycode_homograph.py         9      0      4      0   100%
analyzer/rules/suspicious_keywords.py        9      0      2      0   100%
analyzer/rules/suspicious_tld.py             9      0      2      0   100%
analyzer/rules/url_length.py                 8      0      2      0   100%
analyzer/rules/url_shortener.py             10      0      4      0   100%
analyzer/scorer.py                          52      2     14      0    97%   84-85
analyzer/url_normalizer.py                  70      5     22      1    93%   52, 75-76, 97-98
------------------------------------------------------------------------------------
TOTAL                                      323      7     76      1    98%
```

### Linhas sem cobertura

- [`analyzer/scorer.py`, linhas 84–85](../../analyzer/scorer.py#L84): são o caminho de exceção de `_points_for`, executado quando um motivo não existe em `config.POINTS`. Nenhum dos 251 testes produziu esse motivo desconhecido; a exceção protege contra divergência entre os códigos de motivo e a configuração.
- [`analyzer/url_normalizer.py`, linha 52](../../analyzer/url_normalizer.py#L52): rejeita host vazio após a canonicalização. As URLs inválidas testadas não passaram por esse estado específico.
- [`analyzer/url_normalizer.py`, linhas 75–76](../../analyzer/url_normalizer.py#L75): caminho de erro quando a conversão IDNA de um host Unicode levanta `UnicodeError`. Os casos cobertos não incluíram um host Unicode não conversível.
- [`analyzer/url_normalizer.py`, linhas 97–98](../../analyzer/url_normalizer.py#L97): caminho de erro quando `urlparse` levanta `ValueError`. Nenhum caso da suíte provocou essa exceção de parsing.

As linhas indicadas são caminhos de exceção para entradas ou estados inválidos específicos que não foram exercitados pelos casos desta execução. Isso explica a ausência de cobertura observada; não altera o resultado dos testes aprovados.

## 4. Trechos finais dos logs

### Local

Fonte: `logs/harness_20261022_205112.log`.

```text
analyzer/url_normalizer.py                  70      5     22      1    93%   52, 75-76, 97-98
------------------------------------------------------------------------------------
TOTAL                                      323      7     76      1    98%
============================= 251 passed in 2.70s ==============================
```

### Docker local

Fonte: `/tmp/phishguard-final-docker-test-794dd4c.log`.

```text
analyzer/url_normalizer.py                  70      5     22      1    93%   52, 75-76, 97-98
------------------------------------------------------------------------------------
TOTAL                                      323      7     76      1    98%
============================= 251 passed in 2.81s ==============================
```

### CI — job `Test Harness (pytest)`

Fonte: log do [job pytest da execução CI](https://github.com/mariisena/phishguard-bootcamp-iii/actions/runs/39851335526).

```text
2026-10-22T20:44:06.1221436Z tests/unit/test_url_shortener.py::test_encurtador_no_meio_do_host_nao_dispara PASSED [100%]
2026-10-22T20:44:06.1238278Z TOTAL                                      323      7     76      1    98%
2026-10-22T20:44:06.1239360Z ============================= 251 passed in 2.05s ==============================
```

### CI — job `Test Harness (Docker)`

Fonte: log do [job Docker da execução CI](https://github.com/mariisena/phishguard-bootcamp-iii/actions/runs/39851335526).

```text
2026-10-22T20:44:03.7344078Z tests/unit/test_url_shortener.py::test_encurtador_no_meio_do_host_nao_dispara PASSED [100%]
2026-10-22T20:44:03.7350711Z TOTAL                                      323      7     76      1    98%
2026-10-22T20:44:03.7350918Z ============================= 251 passed in 1.00s ==============================
```