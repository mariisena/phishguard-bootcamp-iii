# Registro de Decisões Arquiteturais (ADRs)

Cada ADR registra uma decisão de projeto: o contexto, a decisão, as alternativas consideradas e as
consequências, **incluindo as negativas**. As ADRs ficam abaixo do `docs/SDD.md` na ordem de
prioridade das fontes (ver `CLAUDE.md`): o SDD define o comportamento, e as ADRs justificam como
ele é implementado.

| ADR | Título | Status | Data | Resumo | Principal trade-off |
| --- | --- | --- | --- | --- | --- |
| [0001](0001-linguagem-e-framework.md) | Python 3.11 + FastAPI | Aceita | 2026-09-08 | Python 3.11, FastAPI e Pydantic na camada HTTP; pytest e `TestClient` nos testes. | Versão de Python e dependências precisa ser padronizada entre máquinas. |
| [0002](0002-heuristicas-vs-ml.md) | Heurísticas em vez de Machine Learning | Aceita | 2026-09-08 | Motor de regras explícitas, puras e determinísticas; sem ML e sem reputação externa. | Não detecta padrões novos nem aprende; listas mantidas à mão. |
| [0003](0003-stateless-sem-banco.md) | Serviço stateless, sem banco | Aceita | 2026-09-08 | Allowlist e blocklist em JSON versionado, carregadas uma vez na inicialização. | Mudar as listas exige reiniciar o serviço; sem histórico de análises. |
| [0004](0004-docker-padronizacao-ambiente.md) | Docker e Docker Compose | Aceita | 2026-09-08 | Docker é o ambiente oficial para subir a API e rodar o Test Harness. | Docker vira dependência obrigatória; build inicial mais lento. |
| [0005](0005-agente-ia-claude-code.md) | Claude Code como agente de IA | Aceita | 2026-09-08 | Claude Code com contexto versionado em `CLAUDE.md` e `.claude/rules/`; decisões de produto ficam com o time. | Qualidade depende do contexto estar atualizado; todo código gerado exige revisão humana. |
| [0006](0006-subdominios-sem-public-suffix-list.md) | Subdomínios sem Public Suffix List | Aceita | 2026-09-08 | Os dois últimos labels são o domínio-base; dispara com mais de 3 subdomínios. | Falso positivo em `.com.br`, `.gov.br`, `.co.uk`. |
| [0007](0007-marca-por-inclusao-e-leet-speak.md) | Marca por inclusão + leet speak | Aceita | 2026-09-12 | Marca contida no host após mapa leet fixo, exceto domínio oficial. | Falsos positivos por coincidência (`capitaurbana.com` → `itau`, #91). |
| [0008](0008-contrato-deterministico-sem-checked-at.md) | Contrato determinístico, sem `checked_at` | Aceita | 2026-09-08 | A resposta tem só os 5 campos do SDD §5.2; nada gerado no momento da requisição. | A resposta não informa quando a análise foi feita. |
| [0009](0009-ci-github-actions.md) | CI com GitHub Actions | Aceita | 2026-09-10 | Dois jobs em todo push e PR: pytest com artefato de evidência e `docker compose run --rm test`. | Depende do GitHub Actions; o bloqueio de merge vem do ruleset da `main`/`develop`, que exige os dois jobs. |

As ADRs 0006 a 0009 foram escritas em 2026-10-12 (issue #102) para decisões que já estavam em
vigor no SDD ou no repositório, mas sem registro próprio. A data da tabela é a da decisão; a data
do registro aparece no cabeçalho de cada ADR.

## Revisão de 2026-10-12

As ADRs 0001 a 0005 foram revisadas na Entrega 2. Todas continuam válidas, com status, data,
alternativas e consequências negativas. Ajustes feitos:

* ADR-0002 e ADR-0004 ganharam referência às ADRs que detalham seus trade-offs (0006, 0007 e 0009).
* ADR-0005 passou a citar `.claude/rules/` como parte do contexto versionado (issue #93).

## Como propor uma nova ADR

1. Copie a estrutura de uma ADR existente: Status, Data, Contexto, Decisão, Alternativas
   Consideradas, Consequências (Positivas e Negativas / Trade-offs), Evolução da decisão.
2. Use o próximo número livre e um nome curto em minúsculas com hífens.
3. Se a decisão mudar comportamento, atualize o `docs/SDD.md` antes.
4. Acrescente a linha nesta tabela e o resumo na seção de ADRs do `README.md` principal.
5. Uma ADR substituída não é apagada: o status passa a "Substituída por ADR-XXXX".
