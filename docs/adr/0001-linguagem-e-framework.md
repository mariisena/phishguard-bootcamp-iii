# ADR-0001: Uso de Python 3.11 + FastAPI

**Status:** Aceita
**Data:** 2026-09-08

## Contexto

O PhishGuard precisa expor o serviço de análise de URLs por meio de uma API HTTP, utilizando uma stack que permita:

* implementação simples e modular;
* validação estruturada dos contratos de entrada e saída;
* boa integração com testes automatizados;
* execução local e em contêineres;
* baixo overhead de configuração para um projeto de bootcamp com prazo reduzido.

Além da camada HTTP, a solução precisa favorecer a implementação de regras de negócio como funções isoladas e determinísticas, conforme definido em `docs/SDD.md`, facilitando a construção e execução do Test Harness.

## Decisão

Utilizar **Python 3.11** como linguagem principal da aplicação, **FastAPI** como framework para a camada HTTP e **Pydantic** para definição e validação dos modelos de entrada e saída da API.

Os testes automatizados utilizarão **pytest**, com `TestClient` para os testes de integração da camada HTTP.

## Alternativas Consideradas

* **Node.js + Express:** stack válida e adequada para APIs HTTP, porém a equipe possui maior familiaridade com Python. Além disso, o uso de `pytest` e de funções puras favorece a implementação e o teste das heurísticas baseadas em regras do PhishGuard.

* **Flask:** framework simples e flexível, porém não oferece, por padrão, o mesmo nível de integração entre validação de modelos, documentação OpenAPI e tipagem fornecido pelo conjunto FastAPI + Pydantic. Isso exigiria maior quantidade de código adicional para validação dos contratos.

* **Django + Django REST Framework:** solução robusta, porém inclui recursos como ORM, administração e uma estrutura mais abrangente do que a necessária para esta versão do serviço, que não possui persistência em banco de dados.

## Consequências

### Positivas

* Os modelos Pydantic permitem validar de forma estruturada os contratos JSON definidos em `docs/SDD.md`.

* O FastAPI gera automaticamente uma especificação OpenAPI a partir dos endpoints e modelos implementados, facilitando a inspeção do contrato efetivamente exposto pela aplicação e a identificação de divergências em relação ao SDD.

* Os testes de integração da API podem utilizar `TestClient`, sem necessidade de iniciar manualmente um servidor HTTP externo durante a execução da suíte.

* Python facilita a implementação das heurísticas como funções puras e independentes, favorecendo os requisitos de modularidade, determinismo e testabilidade definidos no SDD.

* A stack possui boa integração com `pytest`, permitindo testes unitários, testes de contrato e testes de integração dentro do mesmo ecossistema.

### Negativas / Restrições

* A equipe deve manter a versão do Python e das dependências padronizada para evitar diferenças de comportamento entre ambientes.

* O ambiente de execução deverá utilizar Python 3.11, inclusive nos contêineres Docker, conforme a estratégia de reprodutibilidade definida na ADR correspondente.

* Alterações nos modelos Pydantic ou nos endpoints não substituem a atualização do SDD. Como o projeto segue Spec-Driven Development, qualquer mudança de contrato deve ser documentada primeiro em `docs/SDD.md`.
