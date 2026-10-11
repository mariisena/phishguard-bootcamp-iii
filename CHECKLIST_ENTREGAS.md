# **ENTREGAS PROJETO BOOTCAMP**

## **Sumário**

- [**Atividade: Entrega inicial**](#atividade-entrega-inicial);
- [**Atividade Prática • Etapa INTERMEDIÁRIA**](#atividade-prática--etapa-intermediária);

---

## **Atividade: Entrega inicial**

### Entrega 1: Ambiente, Especificação Técnica e Test Harness

Desenvolvimento Iterativo, Colaboração com IA e Validação Automatizada

#### 🎯 Objetivo da Entrega

Estruturar o ambiente de desenvolvimento colaborativo, definir a arquitetura e especificação de um problema real escolhido pela equipe, configurar agentes de geração de código no fluxo SDD (Spec-Driven Development) e entregar um harness de testes funcional com execução documentada.

#### 📦 Itens Obrigatórios para Entrega

**1 Repositório GitHub e Governança do Projeto?**

1. [X] Estrutura de Branches: Adoção de fluxo de versionamento estruturado (ex: main, develop e feature/*). Proibido commits diretos na branch principal.
2. [X] Trabalho em Equipe: Divisão de tarefas registrada no GitHub Projects/Issues, evidenciando o escopo da sprint e decomposição do problema em tarefas independentes.
3. [X]  Code Review & PRs: Pull Requests contendo histórico de revisões, comentários e aprovações entre os membros antes do merge.
4. [X] Documentação Técnica (README.md): Arquivo principal contendo visão geral do projeto, guia de instalação/execução e um registro sintético de decisões arquiteturais técnicas (ADRs).

**2 Especificação Técnica do Problema (SDD):**

1. [X] Documento de Especificação: Descrição detalhada do problema selecionado, requisitos funcionais e não-funcionais, regras de negócio e contratos de entrada/saída.
2. [X] Decomposição em Unidades: Modelagem de componentes e APIs isoladas para permitir desenvolvimento iterativo e testabilidade.
3. [X] Refinamento por Feedback: Registro de alterações ou ajustes realizados na especificação inicial com base em testes prévios ou revisões do grupo.

**3 Configuração de Agentes de IA e Ambiente Padronizado:**

1. [X] Orquestração de Agentes: Configuração e uso documentado de ao menos uma ferramenta de geração/auxílio de código (Claude Code, Codex CLI, Cursor ou Antigravity).
2. [x] Contexto & Regras: Inclusão no repositório dos arquivos de instrução dos agentes (ex: .cursorrules, prompts globais ou diretrizes de contexto para o fluxo SDD).
3. [X] Empacotamento Inicial: Arquivos de padronização do ambiente de desenvolvimento (ex: Dockerfile, docker-compose.yml ou scripts equivalentes) para garantir reprodutibilidade.

**4 Test Harness & Evidências de Execução:**

- [x] Harness de Validação: Infraestrutura de testes automatizados criada para validar a aplicação conforme a especificação técnica definida.
- [x] Suíte de Testes Inicial: Casos de teste cobrindo cenários principais e casos de borda (edge cases).
- [x] Relatório e Logs de Execução: Documentação comprovando a execução bem-sucedida dos testes (logs anexados no README ou relatório de execução da suite).

#### 📤 Formato e Informações de Submissão

Todos os membros do grupo devem submeter no Moodle um único arquivo em formato PDF contendo:

- [X] Link direto do Repositório Público no GitHub (ou com acesso liberado aos professores).
- [X] Nomes completos e RAs de todos os integrantes da equipe.
- [X] Resumo explicativo do ambiente, agentes utilizados e comandos para execução do harness.
- [X] Prints/Logs comprobatórios do pipeline de testes rodando no ambiente padronizado.

---

## Atividade Prática • Etapa INTERMEDIÁRIA

### **Entrega 2: Publicação do Projeto, Refinamento e Análise Crítica do Uso de IA**

**Projeto Final no GitHub, Testes Automatizados, Governança e Relatório Ético-Técnico.**

> [!NOTE]
> 🎯 Objetivo da Entrega
> Consolidar e publicar o projeto completo resolvendo os desafios propostos, aplicar correções a partir dos testes automatizados, garantir a governança do repositório em equipe, defender as decisões técnicas tomadas e elaborar uma análise crítica detalhada sobre segurança, ética e limitações dos agentes de IA no ciclo de vida de software.

### **📦 Itens Obrigatórios para Entrega:**

**1. Repositório Final Publicado & Governança de Código:**

- [ ] **Solução Funcional:** Aplicação completa e integrada publicada no repositório oficial do grupo no GitHub, resolvendo o problema real especificado na Entrega 1.
- [ ] **Governança de Branches & PRs:** Histórico comprovado de colaboração em equipe via Feature Branches, Pull Requests detalhados com code review entre pares e critérios claros de aceitação antes de cada merge.
- [ ] **Histórico de Commits e Sprints:** Registros das entregas iterativas, fechamento de issues e organização do trabalho colaborativo.

**2. Refinamento por Testes, Erros Lógicos e Re-especificação:**

- [ ] **Resultados dos Testes Automatizados:** Execução e aprovação completa do test harness abrangendo os cenários normais e de borda.
- [ ] **Inspeção e Correção de Erros Lógicos:** Documentação dos erros identificados durante o ciclo de desenvolvimento e as estratégias adotadas para corrigi-los.
- [ ] **Loop de Re-especificação:** Registro das situações em que a especificação técnica original precisou ser reajustada ou refinada com base nas falhas reveladas pelos testes automatizados ou feedback da equipe.

**3. Comunicação Técnica, Defesa de Projeto & README Final:**

- [ ] **Documentação Completa (README.md):** Instruções claras de instalação e execução em ambiente padronizado, arquitetura da solução e diagrama do fluxo da aplicação.
- [ ] **Defesa das Decisões de Projeto:** Registro Consolidado de Decisões de Arquitetura (ADRs), justificando as escolhas técnicas e trade-offs assumidos.
- [ ] **Relato de Experiência (Comunicação Técnica):** Apresentação sintética (em formato de seção no relatório ou vídeo curto, conforme orientação do professor) cobrindo os aprendizados e desafios do desenvolvimento em grupo.

**4.Análise Comparativa e Avaliação Crítica de IA (Relatório Técnico-Ético):**

- [ ] **Análise Comparativa de Ferramentas:** Matriz ou relatório comparativo entre as ferramentas avaliadas/utilizadas (**Claude Code, Codex CLI, Cursor e/ou Antigravity**), apontando pontos fortes, limitações e impacto real na qualidade das especificações e do código.
- [ ] **Ética, Limites e Segurança do Uso de IA: Discussão crítica fundamentada nos seguintes pilares:**
  - Riscos de alucinação de código e geração de código inseguro ou destrutivo.
  - Vazamento de dados, privacidade e riscos de confidencialidade ao expor contexto aos modelos.
  - Propriedade Intelectual (IP) e direitos autorais do código gerado por IA.
  - A centralidade e obrigatoriedade da **homologação e revisão humana** no fluxo SDD.
  
  > [!IMPORTANT]
  > **📤 Formato e Informações de Submissão**
  >
  > O líder da equipe E os demais membros devem todos enviar via Sala Online um arquivo PDF consolidado contendo:
  > - [ ] Link do Repositório Público do GitHub atualizado com a versão final do código e documentação.
  > - [ ] Identificação dos integrantes (Nome completo e RA).
  > - [ ] Relatório de Execução dos Testes Automatizados demonstrando 100% de passagem.
  > - [ ] Seção de Análise Comparativa e Ético-Técnica sobre Agentes de IA (Item 4).
  > - [ ] Links para Pull Requests relevantes que evidenciem os fluxos de revisão de código em equipe.
  