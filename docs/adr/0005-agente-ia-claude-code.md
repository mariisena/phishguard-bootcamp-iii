# ADR-0005: Claude Code como agente de IA no fluxo SDD

**Status:** Aceita
**Data:** 2026-09-08

## Contexto

A Entrega 1 exige o uso documentado de pelo menos uma ferramenta de Inteligência Artificial para geração, revisão ou auxílio à implementação de código, integrada ao processo de desenvolvimento orientado por especificação.

O projeto utiliza **Spec-Driven Development (SDD)**, no qual requisitos, regras de negócio e contratos devem ser definidos antes da implementação.

Nesse contexto, o uso de uma ferramenta de IA precisa:

* respeitar a especificação como fonte da verdade;
* operar sobre unidades pequenas e testáveis;
* seguir as convenções técnicas do repositório;
* produzir alterações passíveis de revisão humana;
* integrar-se ao fluxo de branches, commits e Pull Requests;
* manter contexto e instruções versionados;
* permitir que o processo de uso da IA seja auditável durante a avaliação da entrega.

Sem um contexto persistente no repositório, diferentes interações com o agente poderiam gerar código baseado em convenções ou interpretações inconsistentes.

## Decisão

Adotar o **Claude Code** como agente de IA principal utilizado pelo time durante esta versão do projeto.

O repositório deverá conter o arquivo:

```text
CLAUDE.md
```

na raiz, responsável por fornecer ao agente o contexto necessário para trabalhar no PhishGuard.

Esse arquivo deverá documentar, no mínimo:

* objetivo do projeto;
* arquitetura e decomposição dos componentes;
* fluxo obrigatório de Spec-Driven Development;
* convenções de código;
* regras para implementação das heurísticas;
* regras para testes;
* contratos e tratamento de erros;
* estrutura de branches;
* padrão de commits;
* requisitos para Pull Requests;
* comportamentos que o agente não pode alterar sem confirmação humana.

A documentação sobre o uso de agentes de IA no projeto ficará registrada em:

```text
docs/AI_AGENTS.md
```

O arquivo `CLAUDE.md` será considerado parte do contexto operacional do projeto, enquanto `docs/SDD.md` continuará sendo a **fonte da verdade para requisitos, regras de negócio e contratos da aplicação**.

A hierarquia esperada é:

```text
docs/SDD.md
     │
     ▼
ADRs vigentes
     │
     ▼
CLAUDE.md
     │
     ▼
Agente de IA
     │
     ▼
Testes + Implementação
     │
     ▼
Revisão humana
```

O agente não poderá substituir decisões de produto, decisões arquiteturais ou revisão humana.

## Fluxo de uso do agente

O uso do Claude Code deverá seguir o fluxo definido pelo projeto:

```text
Especificar
    │
    ▼
Decompor
    │
    ▼
Criar ou atualizar testes
    │
    ▼
Usar o agente para auxiliar a implementação
    │
    ▼
Executar o Test Harness
    │
    ▼
Revisar alterações
    │
    ▼
Pull Request
    │
    ▼
Revisão humana
```

Para mudanças de comportamento, o agente não deverá iniciar diretamente pela implementação.

A sequência esperada é:

1. consultar `docs/SDD.md`;
2. verificar se o comportamento desejado já está especificado;
3. atualizar a especificação primeiro quando necessário;
4. implementar ou ajustar testes;
5. implementar a unidade correspondente;
6. executar a suíte completa;
7. revisar divergências entre especificação, testes e código;
8. submeter a alteração ao fluxo normal de Pull Request.

## Papel do `CLAUDE.md`

O arquivo `CLAUDE.md` deverá funcionar como instrução persistente e versionada para o agente.

Ele deve reduzir a necessidade de repetir manualmente, a cada interação, regras como:

```text
- spec antes de código;
- uma heurística por arquivo;
- funções puras;
- ausência de rede;
- uso de InvalidURLError;
- respostas HTTP 422 para validação;
- constantes centralizadas;
- testes positivo, negativo e de borda;
- proibição de commit direto em main.
```

As instruções contidas no arquivo também servem como referência para integrantes humanos do projeto.

Alterações relevantes no processo de trabalho com agentes de IA deverão ser refletidas no `CLAUDE.md` e versionadas no repositório.

## Alternativas Consideradas

### Cursor

Cursor oferece um ambiente de desenvolvimento com IA integrada diretamente ao editor e permite geração e edição contextual de código.

Foi considerado adequado tecnicamente, porém o time optou pelo Claude Code por preferir um fluxo orientado a terminal e CLI.

Esse modelo se integra naturalmente ao processo utilizado no projeto, incluindo:

* navegação pelo repositório;
* execução de testes;
* inspeção de arquivos;
* criação de alterações pequenas;
* uso de Git;
* preparação de commits e Pull Requests.

Cursor permanece como alternativa válida, mas não será a ferramenta principal documentada nesta entrega.

### Codex CLI

Codex CLI também foi considerado uma alternativa válida para interação com o repositório por terminal.

A escolha pelo Claude Code foi baseada principalmente na familiaridade do time com a ferramenta e na decisão de padronizar o contexto utilizado pelos agentes por meio do `CLAUDE.md`.

A decisão não implica que outras ferramentas sejam tecnicamente inadequadas.

### Uso de IA sem arquivo de contexto versionado

Também seria possível utilizar uma ferramenta de IA fornecendo instruções manualmente em cada sessão.

Essa abordagem foi rejeitada porque aumentaria o risco de:

* regras diferentes entre sessões;
* perda de contexto;
* implementações inconsistentes;
* esquecimento do fluxo SDD;
* divergências nas convenções de código;
* menor auditabilidade do uso da ferramenta.

O contexto versionado reduz essas inconsistências e permite que alterações nas regras de interação com a IA sejam revisadas pelo mesmo fluxo utilizado pelo restante do projeto.

## Consequências

### Positivas

* O agente recebe contexto consistente sobre o projeto ao trabalhar no repositório.

* As regras do fluxo SDD permanecem versionadas e podem ser revisadas por toda a equipe.

* O agente pode auxiliar na implementação de unidades pequenas e testáveis sem depender de longas explicações manuais em cada interação.

* A relação entre:

```text
Especificação → Teste → Implementação
```

fica explicitamente incorporada às instruções fornecidas ao agente.

* O processo de utilização da IA torna-se mais auditável para a equipe e para os avaliadores da entrega.

* Convenções de arquitetura, código, testes, branches e commits ficam centralizadas em um único arquivo de contexto operacional.

* O agente pode auxiliar em tarefas como:

  * implementação de heurísticas;
  * criação de testes;
  * revisão de código;
  * identificação de divergências;
  * documentação;
  * análise da conformidade entre implementação e SDD.

* Alterações produzidas com auxílio da IA continuam passando pelo mesmo processo de revisão utilizado para código escrito manualmente.

### Negativas / Limitações

* A qualidade das sugestões do agente depende da qualidade e atualização do contexto disponível no repositório.

* Um `CLAUDE.md` desatualizado pode induzir o agente a seguir regras que já não correspondem ao estado atual do projeto.

* O uso da ferramenta não garante que o código gerado esteja correto, seguro ou aderente à especificação.

* Toda alteração produzida por IA ainda precisa ser validada por testes e revisão humana.

* O projeto passa a possuir certa dependência operacional das convenções específicas de contexto utilizadas pelo Claude Code.

* Outras ferramentas de IA podem interpretar instruções de maneira diferente, mesmo utilizando o mesmo conteúdo como referência.

* O uso de IA não elimina a necessidade de conhecimento técnico por parte da equipe.

## Responsabilidade humana

O Claude Code deve ser tratado como uma ferramenta de auxílio ao desenvolvimento, e não como autoridade final sobre o comportamento do sistema.

Decisões humanas continuam sendo obrigatórias para mudanças relacionadas a:

* requisitos;
* regras de negócio;
* pesos das heurísticas;
* limiares de classificação;
* contratos da API;
* novas dependências externas;
* persistência;
* arquitetura;
* segurança;
* escopo da entrega.

O agente não deverá alterar regras especificadas apenas para fazer testes passarem.

Quando houver divergência entre:

```text
SDD
testes
implementação
instruções do agente
```

o problema deverá ser identificado explicitamente antes da alteração do comportamento.

## Revisão de código gerado por IA

Código criado ou alterado com auxílio do agente deverá seguir os mesmos critérios de qualidade aplicados ao código produzido manualmente.

Antes do merge, deverá ser verificado se a alteração:

* corresponde ao requisito correto;
* respeita `docs/SDD.md`;
* respeita as ADRs vigentes;
* segue as convenções do `CLAUDE.md`;
* possui testes suficientes;
* não introduz dependências não autorizadas;
* não altera contratos sem documentação;
* não inclui código desnecessário;
* mantém comportamento determinístico quando aplicável;
* passa pela suíte completa do Test Harness.

A autoria assistida por IA não reduz a responsabilidade da equipe sobre o código incorporado ao projeto.

## Rastreabilidade

O uso da IA deverá favorecer tarefas pequenas e rastreáveis.

Sempre que possível, cada alteração deverá permitir identificar claramente:

```text
Requisito ou regra
        │
        ▼
Prompt/tarefa
        │
        ▼
Alteração de código
        │
        ▼
Teste correspondente
        │
        ▼
Commit
        │
        ▼
Pull Request
```

Prompts representativos utilizados pelo time poderão ser registrados em `docs/AI_AGENTS.md` como evidência do processo adotado durante o desenvolvimento.

Não é necessário armazenar todas as interações realizadas com a ferramenta, desde que exista documentação suficiente para demonstrar como ela foi integrada ao fluxo SDD.

## Manutenção do contexto

O `CLAUDE.md` deverá ser atualizado sempre que houver mudança relevante em:

* arquitetura;
* processo de desenvolvimento;
* estrutura do projeto;
* estratégia de testes;
* contratos;
* regras de trabalho;
* fluxo Git;
* responsabilidades atribuídas ao agente.

Mudanças de requisitos e regras de negócio devem continuar sendo realizadas primeiro em `docs/SDD.md`.

O `CLAUDE.md` deve refletir essas decisões, mas não substituí-las.

## Evolução da decisão

O time poderá adotar outras ferramentas de IA futuramente.

A utilização de outro agente não exige necessariamente abandonar o Claude Code, desde que:

* a nova ferramenta respeite o fluxo SDD;
* utilize contexto compatível com as regras do projeto;
* as alterações continuem sendo revisadas por humanos;
* o processo permaneça rastreável e auditável.

Caso o agente principal do projeto seja substituído ou o modelo de uso de IA seja alterado significativamente, esta ADR deverá ser revisada ou substituída por uma nova decisão arquitetural.

Até que isso ocorra, o **Claude Code**, utilizando o contexto versionado em `CLAUDE.md`, permanece como o agente de IA principal do fluxo de desenvolvimento do PhishGuard.
