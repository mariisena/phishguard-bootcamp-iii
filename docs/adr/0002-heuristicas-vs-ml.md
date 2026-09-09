# ADR-0002: Motor de regras heurísticas em vez de Machine Learning (v1)

**Status:** Aceita
**Data:** 2026-09-08

## Contexto

A detecção de phishing em URLs pode ser realizada por diferentes abordagens, entre elas:

* modelos de Machine Learning treinados com conjuntos de URLs legítimas e maliciosas;
* consultas a serviços externos de reputação;
* regras heurísticas explícitas baseadas em características estruturais e léxicas da URL.

Para a primeira versão do PhishGuard, a solução precisa atender especialmente aos requisitos de:

* determinismo;
* explicabilidade;
* rastreabilidade entre requisito, implementação e teste;
* execução local, sem dependência de serviços externos;
* baixo custo de implementação e manutenção durante o Bootcamp;
* facilidade para criação de um Test Harness automatizado.

O projeto segue **Spec-Driven Development (SDD)**, portanto o comportamento esperado deve ser definido explicitamente na especificação e validado por testes automatizados.

## Decisão

Para esta versão do PhishGuard, utilizar um **motor de regras heurísticas explícitas, determinísticas e explicáveis**, conforme as heurísticas definidas em `docs/SDD.md`.

Cada heurística deverá ser implementada como uma unidade independente e testável, utilizando uma interface comum equivalente a:

```python
def check(parsed: ParsedURL) -> HeuristicResult:
    ...
```

As heurísticas deverão ser funções puras:

* sem efeitos colaterais;
* sem acesso à rede;
* sem dependência de horário ou estado externo;
* com o mesmo resultado para a mesma entrada e configuração.

O `scorer` será responsável por executar as heurísticas, agregar suas pontuações e aplicar as regras de classificação definidas no SDD.

Machine Learning e consultas externas de reputação **não serão utilizados nesta versão**.

## Alternativas Consideradas

### Modelo de Machine Learning

Exemplo: Random Forest ou outro classificador treinado a partir de características léxicas e estruturais extraídas das URLs.

Essa abordagem poderia capturar padrões mais complexos do que regras fixas, porém exigiria:

* dataset rotulado de URLs legítimas e maliciosas;
* processo de limpeza e preparação dos dados;
* definição e extração de *features*;
* pipeline de treinamento;
* métricas de avaliação do modelo;
* tratamento de *overfitting* e qualidade do dataset;
* versionamento do modelo;
* estratégia para reprodutibilidade do treinamento;
* critérios adicionais para explicar e testar as decisões produzidas.

Essas necessidades aumentariam significativamente o escopo da Entrega 1.

Além disso, o motor de regras permite uma correspondência mais direta entre:

```text
Requisito → Regra → Implementação → Teste → Motivo da resposta
```

Essa rastreabilidade é especialmente adequada ao fluxo SDD adotado pelo projeto.

Machine Learning permanece como possível evolução futura, caso exista necessidade, dataset adequado e uma nova decisão arquitetural que defina seu papel no sistema.

### Serviço externo de reputação

Exemplos:

* Google Safe Browsing;
* VirusTotal;
* outros serviços de *threat intelligence* ou reputação de URLs.

Essa abordagem poderia melhorar a identificação de URLs já conhecidas como maliciosas, mas introduziria:

* dependência de rede;
* aumento de latência;
* necessidade de credenciais ou chaves de API;
* possíveis limites de requisição;
* dependência da disponibilidade de terceiros;
* resultados que podem variar ao longo do tempo;
* maior complexidade para testes determinísticos.

O uso de serviços externos fica fora do escopo desta versão.

Caso seja adotado futuramente, deverá ser documentado por uma nova ADR ou pela atualização formal da decisão arquitetural correspondente.

## Consequências

### Positivas

* Cada heurística pode ser diretamente rastreada aos requisitos e regras definidos em `docs/SDD.md`.

* O Test Harness pode testar cada regra isoladamente com casos positivos, negativos e de borda.

* O resultado da análise é determinístico para a mesma entrada e configuração.

* A aplicação pode executar toda a análise localmente, sem chamadas de rede externas.

* A resposta da API é explicável: o campo `reasons` identifica quais sinais de risco contribuíram para a avaliação.

* Novas heurísticas podem ser adicionadas de forma modular, sem necessidade de alterar as regras existentes, desde que respeitem a interface comum definida pelo projeto.

* Falhas em uma regra específica são mais simples de localizar e reproduzir durante testes.

### Negativas / Limitações

* Regras heurísticas fixas podem não detectar novos padrões de phishing que não estejam representados na especificação.

* A solução pode produzir falsos positivos ou falsos negativos caso os critérios e pesos utilizados não representem adequadamente determinados cenários.

* Listas como TLDs suspeitos, encurtadores, marcas monitoradas e palavras-chave precisam ser mantidas manualmente.

* A solução não possui, nesta versão, conhecimento sobre a reputação real e atual de um domínio na internet.

* O motor heurístico não aprende automaticamente com novos exemplos de ataques.

## Evolução da decisão

As heurísticas poderão evoluir conforme novos requisitos e feedback forem incorporados ao projeto.

Mudanças de comportamento deverão seguir o fluxo SDD:

```text
Especificar → Testar → Implementar → Validar
```

Alterações em regras existentes, inclusão de novas heurísticas ou ajustes relevantes de comportamento devem ser registrados no histórico ou na seção de **Refinamento por Feedback** de `docs/SDD.md`.

A adoção futura de Machine Learning ou de serviços externos de reputação deverá ser tratada como uma decisão arquitetural explícita, com análise própria de benefícios, custos, impacto no determinismo, testabilidade e operação do sistema.
