# Análise Comparativa das Ferramentas de IA

Matriz comparativa das ferramentas de IA usadas pelo grupo no PhishGuard, com pontos fortes, limitações e impacto real na especificação e no código (issue #104).

## Fonte e método

Esta análise se baseia **somente no uso real** relatado pelos integrantes nos comentários da [issue #104](https://github.com/mariisena/phishguard-bootcamp-iii/issues/104) e em evidências verificáveis no repositório (commits, PRs e issues). Não foram usados materiais de divulgação das ferramentas.

| Integrante | Ferramentas relatadas | Relato |
| ---------- | --------------------- | ------ |
| [mariisena](https://github.com/mariisena) | Claude Code (Opus 5.5), na extensão do VS Code | [comentário na #104](https://github.com/mariisena/phishguard-bootcamp-iii/issues/104) |
| [mhsilvaworks](https://github.com/mhsilvaworks) | Claude e Gemini, pela interface web | [comentário na #104](https://github.com/mariisena/phishguard-bootcamp-iii/issues/104) |
| [anaacllara](https://github.com/anaacllara) | Google Antigravity; GitHub Copilot no VS Code e no Codespaces; Claude pela interface web | [comentário na #104](https://github.com/mariisena/phishguard-bootcamp-iii/issues/104) |
| [Henrique-GG](https://github.com/Henrique-GG) | Não registrou relato na issue | — |

**Ferramentas citadas na issue e não usadas:** ninguém relatou uso de **Codex CLI** nem de **Cursor**. Por isso, essas duas aparecem na matriz como "não usada" e não recebem avaliação. A [ADR-0005](../adr/0005-agente-ia-claude-code.md) registra as duas como alternativas consideradas e não adotadas.

**Agrupamento:** o relato de mhsilvaworks avalia Claude e Gemini web em conjunto, sem separar uma ferramenta da outra. Para não inventar diferenças, os dois aparecem numa única coluna, **Chat web**, que também reúne o uso do Claude web por anaacllara.

**Escala usada nas células:**
- **Forte:** o relato descreve resultado positivo, com exemplo.
- **Parcial:** há resultado positivo, mas com limitações relatadas.
- **Fraco:** o relato descreve mais problemas do que benefícios.
- **Sem relato:** a ferramenta foi usada, mas ninguém avaliou esse critério.
- **Não usada:** ninguém do grupo usou a ferramenta.

## Matriz

| Critério | Claude Code | Chat web (Claude, Gemini) | Antigravity | GitHub Copilot (VS Code, Codespaces) | Codex CLI | Cursor |
| -------- | ----------- | ------------------------- | ----------- | ------------------------------------ | --------- | ------ |
| Aderência às regras (`CLAUDE.md`, SDD) | **Forte**: leu `CLAUDE.md` e `.claude/rules/` e não mudou pesos, listas, contratos nem a `main` por conta própria | **Parcial**: perdeu o contexto da árvore de arquivos e teve alucinações de contexto; exigiu prompts muito detalhados | **Parcial**¹: desalinhamento com o SDD no início, que melhorou com arquivos de contexto e prompts estruturados | **Parcial**¹: mesma observação | Não usada | Não usada |
| Qualidade do código gerado | **Forte**: refatorou heurísticas para o contrato `check(parsed)` e corrigiu imports quebrados escritos por uma pessoa | Sem relato (usado para documentação) | **Parcial**¹: gerou funções e testes, mas com imports e dependências inadequados | **Parcial**¹: refinou testes; mesmas ressalvas | Não usada | Não usada |
| Escrita e revisão da especificação | **Forte**: revisão de consistência do SDD v1.3 | **Forte**: "altamente eficaz" para estruturar prompts, especificações e documentos técnicos | Sem relato | **Parcial**: usado para refinar as especificações finais da Entrega 2, sem avaliação detalhada | Não usada | Não usada |
| Revisão de código e divergências | **Forte**: encontrou issues fechadas sem entrega (#97, #118) e links quebrados (#96), sempre a partir de um problema pedido | Sem relato | **Fraco**¹: não apontou divergências de arquitetura sem direcionamento explícito | **Fraco**¹: mesma observação | Não usada | Não usada |
| Integração com o fluxo (terminal, IDE, git, PR) | **Forte**: cria branch, commita, abre PR, confere CI e roda Docker, tudo com aprovação manual | **Parcial**: copiar e colar para o VS Code; menos prático, mas cada bloco foi auditado antes de entrar | **Parcial**: ajudou a descrever problemas e PRs; git conduzido manualmente | **Fraco**: no Codespaces, modificou arquivos sem pedir permissão | Não usada | Não usada |
| Custo, acesso e curva de aprendizado | **Forte**: plano Pro, sem esgotar o limite; ensinou o que fazer e como fazer | Sem relato de custo | **Fraco**: sem assinatura paga, a cota esgotava com frequência e exigia trocar de modelo manualmente | **Forte**: custo baixo pelo plano de estudante do GitHub | Não usada | Não usada |

¹ O relato de anaacllara descreve esse critério para "as ferramentas" ou "os agentes" em geral, sem separar Antigravity de Copilot. A mesma avaliação foi repetida nas duas colunas e deve ser confirmada pela autora.

## Detalhes por ferramenta

### Claude Code

**Quem usou e como:** mariisena, com o modelo Opus 5.5 na extensão do VS Code, com acesso ao terminal, ao git, ao `gh`, ao Docker e à suíte de testes. Foi usado principalmente para revisão geral do trabalho e, na Entrega 2, para revisão, issues e PRs.

**Pontos fortes**
- **Seguiu o contexto versionado.** É a única ferramenta do grupo que carrega o `CLAUDE.md` e o `.claude/rules/` automaticamente, como prevê a ADR-0005.
- **Encontrou divergências encadeadas.** A partir de um problema pedido, chegou a outros ligados a ele.
- **Operou o fluxo git e GitHub de ponta a ponta,** com aprovação manual em cada passo.

**Limitações**
- Precisou de direcionamento: os problemas foram encontrados a partir do que foi pedido, não por varredura espontânea.
- Erros menores de execução: nesta entrega, um commit falhou no PowerShell e a branch foi enviada sem ele. Foi refeito antes do PR (#122).

**Exemplos rastreáveis**
- `1017283`: revisão de consistência do SDD v1.3 ([PR #85](https://github.com/mariisena/phishguard-bootcamp-iii/pull/85))
- `d1b07c8`: migração das heurísticas para o contrato `check(parsed)`
- `6aac06e`: correção de imports quebrados escritos por uma pessoa
- [PR #122](https://github.com/mariisena/phishguard-bootcamp-iii/pull/122): evidência do Docker que faltava depois que a [#118](https://github.com/mariisena/phishguard-bootcamp-iii/issues/118) foi fechada
- No total, é coautor de 30 commits, 18 deles em `analyzer/` ou `tests/`, e é citado em 16 PRs e 18 issues, sempre com o aviso de revisão humana obrigatória.

### Chat web (Claude e Gemini)

**Quem usou e como:** mhsilvaworks usou Claude e Gemini, e anaacllara usou Claude, ambos pela interface web. O conteúdo era transferido manualmente para o VS Code.

**Pontos fortes**
- Escrita técnica e estruturação de documentos em Markdown.
- Lapidação de prompts e especificações antes de repassá-los aos agentes de implementação.
- Controle máximo: cada bloco era auditado antes de entrar no repositório.

**Limitações**
- Não manteve o contexto da árvore de arquivos a longo prazo, o que gerou alucinações de contexto.
- Exigiu reeditar os prompts várias vezes, com instruções muito detalhadas.
- Copiar e colar é menos prático do que um agente integrado.

**Exemplos rastreáveis (mhsilvaworks)**
- [PR #107](https://github.com/mariisena/phishguard-bootcamp-iii/pull/107): relatório de ética e uso de IA
- [PR #108](https://github.com/mariisena/phishguard-bootcamp-iii/pull/108): loop de re-especificação

### Google Antigravity

**Quem usou e como:** anaacllara, para gerar código a partir de arquivos existentes.

**Pontos fortes**
- Ajudou a estruturar a lógica e a gerar funções e testes.

**Limitações**
- Sem assinatura paga, a cota esgotava com frequência e exigia trocar de modelo manualmente.
- Gerou imports ou dependências inadequados, corrigidos na validação humana.¹

**Exemplos rastreáveis:** ⚠️ **a confirmar pela autora.** Os PRs de anaacllara na Entrega 2 são [#113](https://github.com/mariisena/phishguard-bootcamp-iii/pull/113), [#114](https://github.com/mariisena/phishguard-bootcamp-iii/pull/114), [#115](https://github.com/mariisena/phishguard-bootcamp-iii/pull/115), [#116](https://github.com/mariisena/phishguard-bootcamp-iii/pull/116), [#117](https://github.com/mariisena/phishguard-bootcamp-iii/pull/117) e [#119](https://github.com/mariisena/phishguard-bootcamp-iii/pull/119), mas o relato não diz qual ferramenta foi usada em cada um.

### GitHub Copilot (VS Code e Codespaces)

**Quem usou e como:** anaacllara, para refinar testes e as especificações finais da Entrega 2.

**Pontos fortes**
- Custo baixo, pelo plano de estudante do GitHub.

**Limitações**
- No Codespaces, teve comportamento autônomo excessivo: modificou arquivos diretamente sem pedir permissão.

**Exemplos rastreáveis:** ⚠️ **a confirmar pela autora**, pelos mesmos motivos da seção anterior.

### Codex CLI e Cursor

Nenhum integrante usou essas ferramentas no projeto, então não há base para avaliá-las. A ADR-0005 explica por que o grupo escolheu o Claude Code: preferência por um fluxo orientado a terminal, familiaridade do time e padronização do contexto pelo `CLAUDE.md`.

## Incidentes sem ferramenta identificada

O [relatório de ética](etica_seguranca.md) registra dois incidentes com agente de IA: um `taskkill` que encerrou todos os processos Python da máquina e um comando git mal digitado que criou o arquivo `h --force-with-lease`. Pelos relatos da #104, **eles não ocorreram no uso do Claude Code**, e o grupo não identificou qual ferramenta estava envolvida. Por isso, os incidentes não foram atribuídos a nenhuma coluna da matriz. Foi o Claude Code que encontrou o arquivo `h --force-with-lease` no repositório e alertou sobre ele. Depois desses episódios, o grupo criou as regras de `.claude/rules/seguranca.md`.

## Conclusão: quando usar cada uma

| Situação | Ferramenta indicada pela experiência do grupo | Por quê |
| -------- | ---------------------------------------------- | ------- |
| Revisar o repositório contra o SDD, abrir PRs, conferir CI | Claude Code | Lê o contexto versionado e opera o fluxo git, com aprovação humana em cada passo |
| Redigir e lapidar especificações, prompts e relatórios | Chat web (Claude, Gemini) | Bom para texto; o controle manual compensa a falta de contexto do repositório |
| Gerar código a partir de arquivos existentes | Antigravity ou Copilot, com revisão | Acelera a base técnica, mas imports e aderência ao SDD precisaram de correção |
| Trabalho em ambiente remoto (Codespaces) | Copilot, com cuidado | Acesso barato, mas modificou arquivos sem permissão |

**Impacto real observado**
1. **A IA acelerou o trabalho, mas não substituiu a revisão.** Os três relatos concluem que a revisão humana foi indispensável.
2. **O contexto versionado fez diferença.** A ADR-0005 define o Claude Code como agente principal, mas na prática só um integrante o usou. Os problemas de aderência e de contexto apareceram nas ferramentas que não carregam o `CLAUDE.md` automaticamente (chat web, Antigravity, Copilot). Isso é **consistente com** a decisão da ADR-0005, mas não é uma comparação controlada: as ferramentas foram usadas em tarefas diferentes.
3. **Ter autonomia exige limites explícitos.** O agente que modificou arquivos sem permissão (Copilot no Codespaces) e os incidentes sem ferramenta identificada levaram às regras de `.claude/rules/seguranca.md`.

## Referências

- [ADR-0005: Claude Code como agente de IA](../adr/0005-agente-ia-claude-code.md)
- [`docs/AI_AGENTS.md`](../AI_AGENTS.md): orquestração dos agentes no fluxo SDD
- [Relatório de ética e segurança](etica_seguranca.md)
- [Issue #104](https://github.com/mariisena/phishguard-bootcamp-iii/issues/104): relatos originais dos integrantes

---

<sub>Documento consolidado pelo Claude Code a partir dos relatos da issue #104, a pedido de @mariisena. Exige revisão humana; as células marcadas com ⚠️ ou ¹ dependem de confirmação da autora do relato.</sub>
