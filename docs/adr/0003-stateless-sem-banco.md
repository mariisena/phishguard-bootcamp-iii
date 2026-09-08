# ADR-0003: Serviço stateless, sem banco de dados (v1)

**Status:** Aceita
**Data:** 2026-09-08

## Contexto

O PhishGuard precisa verificar os domínios analisados contra uma `allowlist` e uma `blocklist`, conforme definido em `docs/SDD.md`.

Essas listas podem ser armazenadas e consultadas de diferentes formas, incluindo:

* banco de dados relacional;
* armazenamento em memória, como Redis;
* arquivos locais versionados junto ao código.

Para esta versão, o serviço possui um conjunto pequeno e controlado de domínios e não exige:

* atualização das listas em tempo real;
* histórico de análises;
* armazenamento de resultados;
* cadastro de usuários;
* persistência de estado entre requisições.

Além disso, o projeto prioriza determinismo, simplicidade de infraestrutura, reprodutibilidade e facilidade de execução do Test Harness.

## Decisão

Manter o PhishGuard como um **serviço stateless, sem banco de dados**, nesta versão.

As listas de domínios serão armazenadas em arquivos JSON locais:

```text
data/allowlist.json
data/blocklist.json
```

Os arquivos serão carregados em memória durante a inicialização da aplicação e utilizados nas análises subsequentes.

As listas carregadas serão tratadas como dados de configuração imutáveis durante a execução do processo.

Nenhuma requisição deverá modificar `allowlist`, `blocklist` ou qualquer outro estado persistente.

As verificações deverão utilizar o domínio após a normalização definida em `docs/SDD.md`.

Nesta versão:

```text
Request
   │
   ▼
Normalização da URL
   │
   ▼
Consulta às listas em memória
   │
   ▼
Heurísticas + Scoring
   │
   ▼
Response
```

Nenhum resultado da análise será persistido após a resposta da requisição.

## Definição de stateless

Neste contexto, **stateless** significa que o resultado de uma requisição não depende de requisições anteriores.

O serviço pode manter em memória dados de configuração carregados durante sua inicialização, como `allowlist` e `blocklist`, desde que esses dados:

* não sejam modificados pelas requisições;
* sejam os mesmos para todas as análises realizadas pelo processo;
* tenham origem em arquivos versionados e controlados;
* não representem estado de sessão ou histórico de uso.

Assim, duas requisições iguais, executadas com a mesma versão do código, configuração e listas, devem produzir o mesmo resultado relevante de análise.

## Alternativas Consideradas

### PostgreSQL

Um banco relacional como PostgreSQL permitiria:

* armazenar grandes volumes de domínios;
* atualizar listas sem alterar arquivos do repositório;
* manter histórico das alterações;
* realizar consultas mais complexas;
* persistir resultados de análises futuramente.

Entretanto, para a Entrega 1, sua adoção introduziria complexidade desnecessária, incluindo:

* contêiner adicional;
* configuração de conexão;
* gerenciamento de credenciais;
* migrations;
* inicialização de dados;
* banco específico para testes;
* fixtures adicionais;
* maior quantidade de pontos de falha.

O volume atual de dados não justifica esse custo operacional.

### Redis

Redis permitiria consultas rápidas e atualização dinâmica das listas em memória.

Entretanto, a quantidade de registros desta versão é pequena e pode ser consultada eficientemente utilizando estruturas nativas do Python.

Sua adoção também introduziria:

* serviço adicional;
* conexão externa ao processo da aplicação;
* configuração adicional no Docker Compose;
* dependência operacional;
* maior complexidade na execução do Test Harness.

Para o volume e os requisitos atuais, o benefício seria mínimo.

### Arquivos locais carregados a cada requisição

Também seria possível ler `allowlist.json` e `blocklist.json` a cada análise.

Essa alternativa foi rejeitada porque introduziria I/O desnecessário no caminho crítico de cada requisição e tornaria o comportamento dependente de alterações no sistema de arquivos durante a execução.

O carregamento único durante a inicialização mantém a análise mais simples e previsível.

## Consequências

### Positivas

* A aplicação não depende de banco de dados ou serviço de armazenamento externo.

* O ambiente Docker possui menos componentes e é mais simples de executar e reproduzir.

* O Test Harness não precisa inicializar banco de dados, executar migrations ou realizar limpeza de estado entre testes.

* `allowlist` e `blocklist` podem possuir versões específicas para testes, permitindo cenários controlados e determinísticos.

* As consultas podem ser realizadas diretamente em memória, evitando I/O de arquivo durante cada análise.

* O comportamento permanece determinístico enquanto forem mantidos:

  * a mesma URL;
  * a mesma versão do código;
  * a mesma configuração;
  * a mesma versão da `allowlist`;
  * a mesma versão da `blocklist`.

* Não existe dependência entre requisições sucessivas.

### Negativas / Limitações

* Alterações realizadas nos arquivos JSON não precisam ser refletidas automaticamente em um processo já em execução.

* Para garantir comportamento previsível nesta versão, mudanças em `allowlist` ou `blocklist` devem ser aplicadas por meio de uma nova inicialização do serviço.

* Não existe mecanismo administrativo para adicionar ou remover domínios em tempo real.

* As alterações das listas dependem do fluxo de versionamento e implantação do projeto.

* Arquivos locais deixam de ser uma solução adequada caso as listas cresçam significativamente ou precisem de atualizações frequentes.

* A aplicação não mantém histórico das análises realizadas.

* Não existe persistência de métricas, resultados ou decisões produzidas pelo serviço nesta versão.

## Tratamento das listas

A lógica responsável pelas listas deverá permanecer isolada no componente:

```text
src/phishguard/blocklist.py
```

Esse componente será responsável por:

* carregar os arquivos locais;
* disponibilizar as estruturas em memória;
* verificar pertencimento de domínios;
* manter a lógica de acesso às listas separada das heurísticas.

As heurísticas não devem abrir ou ler diretamente os arquivos JSON.

O `scorer` deve consumir a interface fornecida pelo componente de listas, respeitando as regras de precedência definidas em `docs/SDD.md`.

Dados utilizados especificamente nos testes devem ser isolados dos dados utilizados pela configuração padrão da aplicação sempre que necessário.

## Relação com determinismo

A ausência de banco de dados e de atualizações dinâmicas reduz fontes externas de variação durante uma análise.

O comportamento do serviço pode ser representado conceitualmente como:

```text
resultado = analyze(
    url,
    configuração,
    allowlist,
    blocklist
)
```

Dadas as mesmas entradas e a mesma versão desses dados, o resultado relevante da análise deve permanecer idêntico.

Isso atende aos requisitos de determinismo e testabilidade definidos no SDD.

## Evolução da decisão

Esta decisão deverá ser revisada caso versões futuras do PhishGuard passem a exigir:

* atualização de listas em tempo real;
* grande volume de domínios;
* armazenamento de resultados;
* histórico de análises;
* auditoria;
* gerenciamento administrativo das listas;
* dados compartilhados dinamicamente entre múltiplas instâncias;
* persistência de usuários ou configurações.

A adoção de PostgreSQL, Redis ou outra solução de persistência deverá ser registrada em uma nova ADR ou em uma revisão formal desta decisão, incluindo impactos em:

* arquitetura;
* infraestrutura;
* determinismo;
* testes;
* desempenho;
* implantação;
* segurança.

Até que uma nova decisão seja registrada, os arquivos JSON locais permanecem como fonte de dados da `allowlist` e `blocklist` do PhishGuard.
