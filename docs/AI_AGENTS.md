# Orquestração de Agentes de IA

Este documento descreve como agentes de Inteligência Artificial são utilizados no desenvolvimento do **PhishGuard** e como esse uso é integrado ao fluxo de **Spec-Driven Development (SDD)** adotado pela equipe.

O objetivo não é delegar decisões de produto ou arquitetura ao agente, mas utilizá-lo como ferramenta de apoio para revisão, decomposição, implementação, testes e identificação de divergências, mantendo as decisões relevantes sob responsabilidade da equipe.

---

## Ferramenta utilizada

A ferramenta de IA principal adotada pelo time é o **Claude Code**, utilizado por meio de CLI durante o desenvolvimento do projeto.

A decisão e suas justificativas estão registradas na ADR correspondente:

```text
docs/adr/0005-agente-ia-claude-code.md
```

O Claude Code é utilizado como ferramenta de apoio em atividades como:

- revisão da especificação;
- identificação de requisitos ambíguos;
- decomposição do sistema em unidades menores;
- criação e revisão de testes;
- implementação de unidades isoladas;
- análise de divergências entre especificação, testes e código;
- apoio à documentação;
- execução e interpretação do Test Harness.

O agente não substitui revisão humana nem possui autoridade para alterar requisitos, regras de
negócio, contratos ou decisões arquiteturais por iniciativa própria.

---

## Contexto e regras versionadas

O contexto fornecido ao agente é mantido no próprio repositório.

### `CLAUDE.md`

Localizado na raiz do projeto:

```text
CLAUDE.md
```

Contém o contexto operacional utilizado pelo agente, incluindo:

- objetivo do projeto;
- arquitetura;
- convenções de código;
- fluxo obrigatório de Spec-Driven Development;
- regras para implementação de heurísticas;
- estratégia de testes;
- tratamento de erros;
- fluxo de branches e Pull Requests;
- padrão de commits;
- exemplos de tarefas;
- alterações que não podem ser realizadas sem confirmação humana.

Esse arquivo também serve como referência para os membros da equipe.

### `docs/SDD.md`

A especificação técnica está localizada em:

```text
docs/SDD.md
```

Esse documento é a **fonte da verdade** para:

- requisitos funcionais;
- requisitos não funcionais;
- regras de negócio;
- contratos de entrada e saída;
- critérios de normalização;
- pontuação;
- classificação;
- casos de teste previstos.

Sempre que uma tarefa envolver comportamento do sistema, o agente deve consultar o requisito ou a
regra correspondente antes da implementação.

O uso do agente não mantém automaticamente o código e a especificação sincronizados. A aderência
entre ambos deve ser verificada por meio de revisão, testes e rastreabilidade.

### ADRs

As decisões arquiteturais relevantes são registradas em:

```text
docs/adr/
```

Antes de propor alterações que afetem arquitetura, dependências externas, persistência, ambiente
de execução ou estratégia de desenvolvimento, o agente deve considerar as ADRs vigentes.

---

## Prioridade das fontes

Ao auxiliar no desenvolvimento, o agente deve considerar a seguinte ordem de prioridade:

1. `docs/SDD.md` — requisitos, regras de negócio e contratos;
2. ADRs vigentes — decisões arquiteturais;
3. `CLAUDE.md` — processo e convenções de trabalho;
4. testes automatizados;
5. implementação existente.

Caso exista divergência entre implementação ou testes e o SDD, o agente deve apontar a
inconsistência antes de modificar o comportamento.

O código existente não deve ser considerado automaticamente correto apenas por já estar
implementado.

---

## Fluxo de trabalho do time com o agente

### 1. Discussão e especificação

A equipe discute o problema e define o comportamento esperado em:

```text
docs/SDD.md
```

O agente pode auxiliar na revisão da especificação, procurando, por exemplo:

- requisitos ambíguos;
- regras contraditórias;
- contratos incompletos;
- casos de borda ausentes;
- requisitos duplicados;
- inconsistências de nomenclatura;
- comportamentos difíceis de testar.

A decisão final sobre requisitos e regras de negócio permanece com os membros da equipe.

O fluxo esperado é:

```text
Discussão humana
      │
      ▼
Especificação
      │
      ▼
Revisão assistida por IA
      │
      ▼
Validação humana
```

---

### 2. Decomposição

Com o comportamento definido, o agente pode auxiliar na decomposição da solução em unidades
isoladas e testáveis.

A estrutura principal prevista pelo projeto inclui:

```text
src/phishguard/
├── api.py
├── models.py
├── url_normalizer.py
├── scorer.py
├── blocklist.py
└── heuristics/
```

As responsabilidades de cada componente devem seguir `docs/SDD.md`.

Uma heurística nova deve permanecer isolada em seu próprio módulo, evitando concentrar regras
específicas dentro de `scorer.py`.

---

### 3. Criação dos testes

Depois que o comportamento estiver especificado, o agente pode auxiliar na geração dos testes
correspondentes.

Toda regra nova deve possuir, sempre que aplicável:

1. caso positivo;
2. caso negativo;
3. caso de borda.

Os testes devem ser derivados da especificação, e não apenas do comportamento atual do código.

Exemplo de relação esperada:

```text
RF/RN no SDD
     │
     ▼
Caso de teste
     │
     ▼
Implementação
```

O agente não deve alterar a regra especificada apenas para fazer um teste passar.

---

### 4. Implementação por unidade

Cada unidade de trabalho deve ser desenvolvida em uma branch própria seguindo o padrão:

```text
feature/<nome-curto>
```

Exemplos:

```text
feature/heuristica-ip-literal
feature/heuristica-tld-suspeito
feature/url-normalizer
feature/api-endpoint-analyze
```

O prompt utilizado com o agente deve, sempre que possível, indicar explicitamente o requisito ou
regra que está sendo implementado.

Exemplo:

```text
Implemente a heurística RF-05 de detecção de IP literal no host,
respeitando o contrato definido em docs/SDD.md e os testes existentes.
```

A implementação deve respeitar a decomposição e as convenções documentadas em `CLAUDE.md`.

---

### 5. Execução do Test Harness

Após a implementação, a suíte completa deve ser executada.

Com Docker:

```bash
docker compose run --rm test
```

Ou utilizando o script local:

```bash
./scripts/run_harness.sh
```

O agente pode ser utilizado para:

- executar os testes;
- interpretar falhas;
- identificar possíveis causas;
- apontar heurísticas sem cobertura;
- verificar divergências entre teste e especificação.

Uma falha de teste não significa automaticamente que a implementação deve ser alterada.

A equipe deve primeiro identificar se o problema está:

```text
na implementação
no teste
ou na especificação
```

---

### 6. Revisão humana via Pull Request

Nenhuma alteração produzida com auxílio de IA deve ser incorporada à branch de integração sem
revisão humana.

O fluxo utilizado pelo time é:

```text
feature/*
    │
    ▼
Pull Request
    │
    ▼
Revisão humana
    │
    ▼
Testes aprovados
    │
    ▼
Aprovação
    │
    ▼
develop
```

Todo Pull Request deve seguir as regras definidas em:

```text
CLAUDE.md
GITHUB_SETUP.md
.github/PULL_REQUEST_TEMPLATE.md
```

Quando houver pipeline de integração contínua configurado para a branch ou Pull Request, os testes
automatizados também deverão passar nesse ambiente antes do merge.

---

### 7. Refinamento por feedback

Quando testes, revisão de código ou discussão da equipe revelarem que o problema está na própria
regra especificada, o SDD deve ser atualizado **antes** da implementação.

O fluxo correto é:

```text
Feedback / problema identificado
          │
          ▼
Revisão de docs/SDD.md
          │
          ▼
Atualização dos testes
          │
          ▼
Atualização da implementação
          │
          ▼
Nova validação
```

Mudanças decorrentes de refinamento devem ser registradas no histórico ou na seção de
**Refinamento por Feedback** do SDD, conforme aplicável.

O fluxo inverso — alterar o código primeiro e posteriormente adaptar a especificação para justificar
o comportamento — deve ser evitado.

---

## Ciclo resumido de orquestração

O processo adotado pode ser representado como:

```text
┌─────────────────────┐
│ Discussão da equipe │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     docs/SDD.md     │
│    Especificação    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Agente de IA      │
│ revisão/decomposição│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       Testes        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Implementação    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Test Harness     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Pull Request      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Revisão humana    │
└─────────────────────┘
```

---

## Exemplos de uso do agente

### Revisão da especificação

```text
Revise docs/SDD.md e identifique requisitos ambíguos, contraditórios
ou que não possuam critérios objetivos para teste.
```

### Implementação de heurística

```text
Implemente a heurística RF-08 de detecção de TLD suspeito em
src/phishguard/heuristics/suspicious_tld.py, respeitando o contrato
de HeuristicResult e os critérios definidos no SDD.
```

### Casos de borda

```text
Crie casos de borda para URLs com Punycode e homógrafos Unicode
com base nos cenários previstos em docs/SDD.md.
```

### Revisão de cobertura

```text
Execute a suíte de testes e identifique quais heurísticas ainda não
possuem casos positivo, negativo e de borda.
```

### Verificação de conformidade

```text
Compare scorer.py com as regras de negócio vigentes em docs/SDD.md
e liste divergências sem modificar os arquivos.
```

### Análise de falha

```text
Analise esta falha de teste e indique se a provável divergência está
na implementação, no teste ou na especificação antes de propor uma
alteração.
```

---

## Comandos utilizados no fluxo

Uma sessão do Claude Code pode ser iniciada na raiz do repositório com:

```bash
claude
```

A partir dessa sessão, o agente pode ser utilizado para trabalhar sobre os arquivos do projeto,
executar comandos permitidos e auxiliar nas etapas descritas neste documento.

Exemplos de instruções:

```text
"Implemente a heurística de detecção de IP literal no host (RF-05), com testes."

"Gere casos de borda para URLs com Punycode e homógrafos Unicode."

"Rode a suíte de testes e resuma quais heurísticas ainda não possuem cobertura suficiente."

"Revise scorer.py contra as regras de negócio vigentes no SDD."
```

---

## Rastreabilidade

O uso do agente deve permitir relacionar uma alteração ao requisito que a originou.

Sempre que possível, a cadeia de rastreabilidade deve ser:

```text
Requisito / Regra
       │
       ▼
Prompt ou tarefa
       │
       ▼
Teste
       │
       ▼
Implementação
       │
       ▼
Commit
       │
       ▼
Pull Request
```

Essa rastreabilidade permite demonstrar que a IA foi utilizada dentro do processo SDD, e não apenas
como um gerador isolado de código.

Prompts representativos ou exemplos de interações podem ser registrados neste documento ou em
evidências complementares da entrega quando necessário.

---

## Responsabilidade humana

Todo código ou documento produzido com auxílio de IA continua sendo responsabilidade da equipe.

Antes de incorporar uma alteração, os membros do projeto devem verificar:

- aderência ao SDD;
- compatibilidade com as ADRs vigentes;
- qualidade da implementação;
- cobertura dos testes;
- ausência de alterações não solicitadas;
- manutenção do determinismo;
- compatibilidade com os contratos da API;
- resultado da suíte automatizada.

O agente não deve tomar decisões autônomas sobre:

- pesos das heurísticas;
- limiares de classificação;
- requisitos;
- regras de negócio;
- contratos;
- persistência;
- serviços externos;
- mudanças arquiteturais relevantes.

Essas decisões exigem validação humana e atualização formal da documentação correspondente.

---

## Outras ferramentas consideradas

Outras ferramentas de IA foram consideradas durante a definição do processo, incluindo:

- Cursor;
- Codex CLI.

A justificativa para adoção do Claude Code como ferramenta principal está registrada em:

```text
docs/adr/0005-agente-ia-claude-code.md
```

A escolha do Claude Code não impede o uso futuro de outras ferramentas, desde que respeitem o fluxo
SDD, as regras versionadas do projeto e a revisão humana.

---

## Regra principal

O uso do agente deve respeitar o seguinte ciclo:

```text
Especificar → Testar → Implementar → Validar → Revisar
```

A IA atua como ferramenta de apoio dentro desse processo.

A especificação continua sendo definida e validada pela equipe, e nenhuma alteração gerada pelo agente deve ser incorporada ao projeto sem testes e revisão humana.
