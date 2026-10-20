# ADR-0009: Integração contínua com GitHub Actions (pytest e Docker)

**Status:** Aceita
**Data:** 2026-09-10 (PR #41, issue #16); registrada como ADR em 2026-10-12

## Contexto

O fluxo SDD do projeto depende de a suíte de testes passar antes de cada merge (`CLAUDE.md`,
"Rodar a suíte completa"). Confiar só na execução local tem dois problemas:

* cada integrante usa uma máquina diferente, e "passa na minha máquina" não garante que passe no
  ambiente oficial (ADR-0004);
* parte do código é escrita com ajuda de IA (ADR-0005), e erros como imports de pacote inexistente
  só aparecem quando o código roda num ambiente limpo.

O repositório já está no GitHub, e o RNF-06 pede evidência persistida da execução dos testes.

## Decisão

Usar **GitHub Actions** com o workflow `.github/workflows/ci.yml`, disparado em `push` para
`main`, `develop` e `feature/**`, e em `pull_request` para `main` e `develop`. São dois jobs
independentes:

| Job | O que faz |
| --- | --- |
| `test-harness` | Instala Python 3.11 e o `requirements.txt` e roda `pytest -v`. Publica `logs_test_harness.txt` e `test-report.xml` (JUnit) como artefato por 30 dias. |
| `docker-harness` | Roda `docker compose run --rm test`, o mesmo comando do ambiente oficial da ADR-0004. |

Um PR só deve ser mergeado com os dois jobs verdes.

## Alternativas Consideradas

### Apenas execução local antes do PR

Sem custo de configuração, mas depende de disciplina individual e não deixa evidência verificável
no PR.

### GitLab CI, CircleCI ou Jenkins

Equivalentes em recurso, mas exigiriam conta, integração ou servidor adicional. O GitHub Actions já
está integrado ao repositório e aos PRs, sem custo para repositório público.

### Um único job (só Docker ou só pytest)

Só pytest seria mais rápido, mas não testaria o `Dockerfile` e o `docker-compose.yml`. Só Docker
validaria o ambiente oficial, mas sem o relatório JUnit publicado como artefato. Os dois jobs rodam
em paralelo, então o custo de tempo é pequeno.

## Consequências

### Positivas

* Todo PR mostra se a suíte passa num ambiente limpo, sem depender de quem abriu o PR.
* O job Docker detecta quebras no empacotamento que a suíte local não pega.
* `logs_test_harness.txt` e `test-report.xml` ficam disponíveis como evidência (RNF-06).
* Código gerado por IA passa pela mesma barreira automática que o código escrito à mão.

### Negativas / Trade-offs

* **O CI informa, mas não bloqueia por si só.** Sem proteção de branch exigindo os checks e uma
  aprovação, um PR vermelho ainda pode ser mergeado. Resolvido pelo ruleset da `main` e da
  `develop` (ver "Evolução da decisão").
* O job `docker-harness` testa o serviço `test` do compose, não o serviço da API. Uma quebra só no
  comando de subida da API (como o `phishguard.api:app` corrigido no PR #87) passou pelo CI.
* Dependência de um serviço de terceiros: se o GitHub Actions estiver fora do ar, não há
  validação automática.
* `requirements.txt` com faixas de versão (`pytest>=8.0`) permite que o CI instale versões
  diferentes ao longo do tempo.
* Não há análise estática (linter, formatação com `black`, varredura de segredos) no pipeline.

## Evolução da decisão

**Situação na release `v3.0.0` (2026-10-20):**

* **(1) feito.** Um ruleset do repositório protege a `main` e a `develop`: exige PR com uma
  aprovação, os checks `Test Harness (pytest)` e `Test Harness (Docker)` verdes e atualizados com a
  branch de destino, e bloqueia force-push e exclusão da branch. Os nomes dos jobs no `ci.yml` não
  podem mudar sem atualizar o ruleset.
* O job `test-harness` passou a publicar também o relatório de cobertura (`coverage.xml` e
  `htmlcov/`), gerado pelo `pytest-cov` configurado no `pytest.ini` (#131).
* **(4) parcial.** Os PRs passam pelo check do GitGuardian (app do GitHub, fora do `ci.yml`).
* (2), (3) e (5) continuam pendentes.

Plano original, em ordem de prioridade: (1) proteção de `main` e `develop` exigindo os dois jobs e uma aprovação
(#94); (2) um passo que suba a API e chame `GET /health`; (3) `black --check` e um linter que
rejeite `except Exception: pass`; (4) varredura de segredos; (5) fixar versões das dependências.
