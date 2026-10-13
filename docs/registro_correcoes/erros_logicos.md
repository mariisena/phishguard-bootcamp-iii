# Inspeção e Correção de Erros Lógicos

> Registro dos erros encontrados durante o desenvolvimento do PhishGuard, de como foram detectados
> e corrigidos, e do que mudou no processo por causa deles.

**Data de elaboração:** 2026-10-12
**Issue de origem:** #99 (parte de #95)
**Fontes:** [`correcoes_10_09.md`](correcoes_10_09.md) (saída bruta da revisão de setembro, mantida
como registro original), issue [#84][i84] (revisão de 11/10) e os PRs citados em cada linha.
**Documentos relacionados:** [`docs/re_especificacao.md`](../re_especificacao.md) (mudanças na
especificação) e [`docs/relatorio_ia/etica_seguranca.md`](../relatorio_ia/etica_seguranca.md)
(análise dos erros de origem IA).

Este documento trata de erros em que **o código ou o processo divergiam do SDD**. Quando a
correção foi mudar a especificação, o caso está no documento de re-especificação.

## Como ler a coluna "Origem"

| Valor | Significado |
| --- | --- |
| **IA** | O código veio de um PR que declara ter sido gerado com auxílio do agente (PR [#40][pr40]). |
| **IA (provável)** | O código entrou no commit [`e6bb0fa`][e6bb0fa] ("versiona o pacote analyzer ainda não commitado"), sem PR de origem. O padrão do erro é típico de alucinação e foi classificado assim no relatório de ética (#105), mas a autoria não ficou registrada. |
| **IA (agente em execução)** | Ação do Claude Code durante uma sessão, não código commitado. |
| **Processo** | Falha de fluxo de trabalho (revisão, fechamento de issue, cobertura), não de código. |
| **Não registrada** | Não há como saber pelo histórico se o trecho foi escrito por pessoa ou com IA. |

---

## 1. Rodada de 10–11/09: scorer, heurísticas, listas e normalizador

**Como foi detectado:** revisão do pacote `analyzer/` comparando o código com o SDD, feita com o
Claude Code a pedido de @mariisena logo depois do PR [#40][pr40]. O pacote não chegava a importar:
`import analyzer.scorer` falhava. Os achados foram numerados (1.1, 1.2...) e a saída bruta ficou em
`correcoes_10_09.md`. As correções entraram nos PRs [#51][pr51] a [#54][pr54], mergeados em
2026-09-11, cada um com teste escrito antes ou junto da correção.

### 1.1 Erros pedidos na issue

| # | Erro | Impacto | Correção | Evidência | Origem | Lição |
| --- | --- | --- | --- | --- | --- | --- |
| E01 | Sintaxe de JavaScript no `return` do `scorer.py` (literal de objeto e tipo inexistente). | O módulo não compilava; nenhuma análise rodava. | `return _result(...)` construindo `AnalysisResult`. | [`7926c2f`][7926c2f], PR [#51][pr51] | IA | Importar e rodar o módulo num ambiente limpo antes de abrir o PR; o CI faz isso desde a ADR-0009. |
| E02 | `score` e `reasons` usados antes de serem definidos (blocos manuais de soma antes do laço). | `NameError` na primeira análise. | Inicialização antes do laço; blocos manuais removidos. | [`7926c2f`][7926c2f], PR [#51][pr51] | IA | Mesma de E01. |
| E03 | Parâmetro `lists=None` usado como objeto, sem carregar as listas padrão. | `AttributeError` em toda chamada sem listas injetadas, que era o caso da API. | `lists if lists is not None else load_domain_lists()`. | [`7926c2f`][7926c2f], PR [#51][pr51] | IA | O caminho padrão (sem injeção) precisa de teste próprio. |
| E04 | RN-06 implementada três vezes, e uma das versões considerava a própria palavra-chave como "outra heurística". | A palavra-chave sensível podia pontuar sozinha (ex.: `https://site.com/login` deixava de ter score 0), o que a RN-06 proíbe. | Uma só implementação: `if keyword_result.triggered and reasons`, avaliada depois das demais heurísticas. | [`7926c2f`][7926c2f], PR [#51][pr51] | IA | Regra condicional precisa de teste negativo exato: palavra-chave sozinha dá 0. |
| E05 | Clamp da RN-01 (0–100) aplicado antes do bônus da palavra-chave. | Score acima de 100 possível. | Clamp movido para o fim da agregação. | [`7926c2f`][7926c2f], PR [#51][pr51] | IA | Testar o valor máximo: soma bruta 130 → 100. |
| E06 | Faixas de classificação escritas à mão (`<= 29`, `<= 59`), duplicadas e diferentes de `config.THRESHOLDS`. | Mudar o limiar no `config.py` não mudaria a classificação. | Bloco removido; só `classify()`, que lê `config.THRESHOLDS`. Criados `SCORE_MIN`/`SCORE_MAX` no `config.py`. | [`7926c2f`][7926c2f], [`f466d2b`][f466d2b], PR [#51][pr51] | IA | Constante de negócio só no `config.py` (regra do `CLAUDE.md`). |
| E07 | `url_shortener.py` importava o pacote inexistente `phishguard`. | O scorer não importava a heurística, então nada rodava. | `phishguard` → `analyzer`. | [`6aac06e`][6aac06e], PR [#51][pr51] | IA (provável) | O nome do projeto não é o nome do pacote. Virou regra em `.claude/rules/codigo.md`. |
| E08 | Códigos de motivo e pesos do `config.py` divergentes da Tabela 4.1: seis pesos errados (ex.: `host_ip` 30 em vez de 25, `palavra_chave` 10 em vez de 20) e `punycode_homograph` com código fora da tabela. | Scores diferentes dos documentados; o exemplo normativo do §5.2 não fechava. | `config.POINTS` alinhado à Tabela 4.1 (decisão humana registrada no PR #51); código do punycode renomeado para `punycode_ou_unicode_suspeito`. | [`f466d2b`][f466d2b], PR [#51][pr51] | IA (provável) | Valor esperado nos testes é literal derivado do SDD, nunca lido do `config.py`. Depois disso veio o `test_config_consistency.py` (PR [#71][pr71]). |
| E09 | Heurísticas `ip_domain`, `at_symbol` e `suspicious_keywords` com `urlparse` próprio sobre a URL crua, assinatura fora do contrato (ex.: `evaluate_ip_domain(str) -> dict \| None`) e `except Exception: pass`. | Comportamento diferente do normalizador (ex.: porta no host); falhas internas viravam "não disparou", ou seja, URL considerada mais segura do que é. Só IPv4 era detectado. | Migração para `check(parsed) -> HeuristicResult`, usando os campos do `ParsedURL`; IPv6 incluído. | [`d1b07c8`][d1b07c8], PR [#51][pr51] | IA | Parsing só no `url_normalizer.py`; nenhum `except` genérico. Virou regra em `.claude/rules/codigo.md`. |

### 1.2 Outros erros da mesma rodada

| # | Erro | Impacto | Correção | Evidência | Origem | Lição |
| --- | --- | --- | --- | --- | --- | --- |
| E10 | Palavra-chave na tupla de heurísticas **e** somada de novo no fim (RN-07). | Pontos contados em dobro. | Palavra-chave fora da tupla, avaliada uma vez. | [`7926c2f`][7926c2f], PR [#51][pr51] | IA | — |
| E11 | Motivos das listas como `dominio_em_allowlist`/`dominio_em_blocklist`. | Contrato diferente do SDD (RN-03/RN-04). | `dominio_allowlist`/`dominio_blocklist`. | [`7926c2f`][7926c2f], PR [#51][pr51] | IA | — |
| E12 | `DEFAULT_DATA_DIR` com `parents[2]` apontando para fora do repositório. | Listas nunca carregadas; se houvesse um `data/` na pasta acima, o serviço usaria listas alheias sem avisar. | Caminho corrigido; JSON malformado passa a levantar `InvalidDomainListError`. | [`510c4f7`][510c4f7], PR [#53][pr53] | IA (provável) | Teste de carga real dos arquivos, não só com listas injetadas. |
| E13 | Allowlist casando por sufixo e sem remover `www.` (RF-15, N-07); arquivos relidos a cada análise (ADR-0003). | `qualquer-coisa.paypal.com` liberado com score 0. | Correspondência exata do host canônico; carga única. | [`510c4f7`][510c4f7], PR [#53][pr53] | IA (provável) | Allowlist é a regra mais perigosa de errar: falso negativo garantido. |
| E14 | Normalizador injetava `http://` em entrada sem esquema (N-03) e deixava vazar `ValueError` de porta inválida. | `www.exemplo.com` aceito e ainda pontuado por `sem_https`; erro 500 em vez de 422 (RF-17). | Rejeição com `InvalidURLError`; porta validada. | [`b291b5f`][b291b5f], PR [#54][pr54] | IA (provável) | O normalizador não tinha nenhum teste. Componente central precisa de teste antes de tudo. |
| E15 | RF-08 (TLD suspeito) sem módulo. | O exemplo normativo do §5.2 dava 55, não 70. | Heurística criada. | [`10b126a`][10b126a], PR [#52][pr52] | Processo | O teste do exemplo normativo (`test_exemplo_normativo_do_sdd`) revelou a lacuna. |

---

## 2. Revisão de 11/10 (issue #84)

**Como foi detectado:** revisão completa da Entrega 1 antes de planejar a Entrega 2, também com o
Claude Code a pedido de @mariisena, comparando código, testes, Docker e documentação com o SDD.
Cada achado virou PR ([#85][pr85] a [#89][pr89]) ou issue.

| # | Erro | Impacto | Correção | Evidência | Origem | Lição |
| --- | --- | --- | --- | --- | --- | --- |
| E16 | `checked_at` ainda devolvido pela API, embora o SDD o tivesse removido do contrato em 08/09. | Resposta não determinística, contra o RNF-02. | Teste de contrato exigindo exatamente os 5 campos, escrito antes; campo removido de `models.py` e `api.py`. | [`334197f`][334197f], PR [#86][pr86]; ADR-0008 | Processo | Ver E19. |
| E17 | `docker-compose.yml` subia `phishguard.api:app`, módulo inexistente. | `docker compose up` não subia a API, o ambiente oficial da ADR-0004. O CI não pegou, porque só roda o serviço `test`. | `analyzer.api:app`; revisor confirmou a subida manualmente. | [`77827a2`][77827a2], PR [#87][pr87] | IA (provável) | Mesmo padrão de E07. O CI precisa testar a subida da API (ADR-0009). |
| E18 | Heurísticas duplicadas fora do git (`ip_literal_host.py`, `sensitive_keywords.py`, `userinfo_symbol.py`, `suspicious_tld(1).py`, `src/heuristics/url_lengh.py`) com códigos fora da Tabela 4.1 (`ip_literal_no_host`, `arroba_na_url`); `userinfo_symbol.py` importava `phishguard.*`. | Risco de alguém commitar a versão errada; contrato divergente. | Arquivos removidos do stage local (não chegaram a ser versionados). | Issue [#84][i84] | IA (provável) | Código gerado e não revisado se acumula fora do git. Arquivo novo entra por PR ou é apagado. |
| E19 | **Issues #56, #57 e #66 fechadas como concluídas sem a correção.** | E16 e E17 ficaram um mês a mais no código; a #66 deixou o SDD §7.1 divergente da pasta `tests/`. | Correção real em #86 e #87; #66 reaberta como decisão em [#92][i92]. | Issue [#84][i84] | Processo | Issue só fecha com evidência (commit, PR ou saída de teste). Virou regra em `.claude/rules/seguranca.md`. |
| E20 | Exemplo do README com score 45 para `http://192.168.0.1/login`. O correto é **55** (25 `host_ip` + 10 `sem_https` + 20 palavra-chave). | Documentação contradiz a API; a classificação (`suspeita`) coincide, o que esconde o erro. | Pendente na issue [#101][i101]. | Issue [#101][i101] | Não registrada | Exemplo de documentação deveria ser gerado pela API ou coberto por teste. |
| E21 | Cinco heurísticas sem teste próprio (RF-07, RF-09, RF-10, RF-12, RF-13). | Só cobertas indiretamente pelo scorer; duas limitações (#90, #91) só apareceram ao escrever os testes. | Casos positivo, negativo e de borda para cada uma. | PR [#88][pr88] | Processo | O teste isolado é onde as ambiguidades da spec aparecem. |
| E22 | Na mesma revisão, o agente encerrou **todos** os processos Python da máquina (`taskkill` por nome) para parar um servidor de teste. Antes, um comando git mal digitado criou o arquivo `h --force-with-lease`. | Nenhum dano permanente (máquina de desenvolvimento), mas poderia ter derrubado trabalho de outras ferramentas. | Arquivo removido; regra de encerrar processo só por PID e confirmar comandos destrutivos. | `.claude/rules/seguranca.md` (#93) | IA (agente em execução) | Erro de ação não aparece no diff. Precisa de regra prévia, não de revisão posterior. |

---

## 3. Estratégias adotadas

| Estratégia | O que é | Erros que teria evitado ou que passou a detectar |
| --- | --- | --- |
| **Teste antes da correção** | O teste do comportamento do SDD é escrito primeiro e precisa falhar contra o código antigo. Ex.: PR #86, onde os dois testes de contrato falharam antes da correção. | E04, E05, E16 |
| **`config.py` como fonte única** | Pesos, limiares, listas e limites do score ficam só em `analyzer/config.py`. | E06, E08 |
| **Teste de consistência SDD ↔ config** | `tests/test_config_consistency.py` lê as tabelas do SDD e compara com o `config.py` (PR #71). | E08 e qualquer divergência futura de lista ou peso |
| **Valores esperados literais** | Os testes escrevem o score esperado com a conta da Tabela 4.1 no comentário, sem ler `config.POINTS`. | E08: um peso alterado por engano quebra a suíte |
| **Revisão por PR** | Todo código entra por PR para `develop`, com template de rastreabilidade e aprovação de outro integrante. | E07, E09, E18 (deveriam ter sido barrados na revisão do PR #40) |
| **CI** | GitHub Actions roda `pytest` e `docker compose run --rm test` em todo PR (ADR-0009). | E01, E02, E03 (o pacote nem importava) |
| **Regras do agente** | `.claude/rules/` com as lições específicas deste projeto (#93). | E07, E09, E19, E22 |
| **Evidência para fechar issue** | Issue só fecha com link para commit, PR ou saída de teste. | E19 |

## 4. Erros de origem IA: resumo para o relatório (#105)

De 22 erros registrados, **17 têm origem IA** (9 em código declarado como gerado com o agente,
7 prováveis e 1 ação do agente em execução), 4 são de processo e 1 não tem origem registrada.
Os de origem IA se concentram em três padrões:

1. **Nome inventado:** pacote `phishguard`, códigos de motivo fora da tabela, tipo inexistente
   (E01, E07, E08, E17, E18).
2. **Atalho que esconde falha:** `except Exception: pass`, parsing próprio, caminho de arquivo
   calculado errado (E09, E12).
3. **Regra de negócio quase certa:** RN-06 que libera a si mesma, clamp na hora errada, contagem
   em dobro (E04, E05, E10). Esses são os mais perigosos, porque o código roda e o resultado
   parece plausível.

Os erros de processo (E19, E21) mostram que a IA não foi a única fonte de falha: a revisão humana
também foi pulada. As mitigações estão na seção 3 e na análise do relatório de ética.

[i84]: https://github.com/mariisena/phishguard-bootcamp-iii/issues/84
[i92]: https://github.com/mariisena/phishguard-bootcamp-iii/issues/92
[i101]: https://github.com/mariisena/phishguard-bootcamp-iii/issues/101
[pr40]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/40
[pr51]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/51
[pr52]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/52
[pr53]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/53
[pr54]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/54
[pr71]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/71
[pr85]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/85
[pr86]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/86
[pr87]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/87
[pr88]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/88
[pr89]: https://github.com/mariisena/phishguard-bootcamp-iii/pull/89
[e6bb0fa]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/e6bb0fa
[6aac06e]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/6aac06e
[f466d2b]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/f466d2b
[d1b07c8]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/d1b07c8
[7926c2f]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/7926c2f
[510c4f7]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/510c4f7
[b291b5f]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/b291b5f
[10b126a]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/10b126a
[334197f]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/334197f
[77827a2]: https://github.com/mariisena/phishguard-bootcamp-iii/commit/77827a2
