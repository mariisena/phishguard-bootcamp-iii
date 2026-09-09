# ADR-0004: Docker e Docker Compose para padronização do ambiente

**Status:** Aceita
**Data:** 2026-09-08

## Contexto

O desenvolvimento do PhishGuard é realizado por diferentes membros da equipe, utilizando máquinas, sistemas operacionais e configurações locais distintas.

Diferenças como:

* sistema operacional;
* versão do Python;
* bibliotecas instaladas;
* variáveis de ambiente;
* ferramentas disponíveis na máquina;
* configuração local do interpretador;

podem causar comportamentos inconsistentes entre ambientes de desenvolvimento e dificultar a reprodução dos testes.

Além disso, a Entrega 1 exige empacotamento inicial da aplicação e reprodutibilidade do ambiente.

O projeto também possui requisitos relacionados a:

* portabilidade;
* execução determinística do Test Harness;
* facilidade de configuração;
* geração reproduzível das evidências de teste.

## Decisão

Utilizar **Docker** e **Docker Compose** como forma padrão de executar o PhishGuard e sua suíte automatizada de testes.

O repositório deverá fornecer:

```text
Dockerfile
docker-compose.yml
requirements.txt
```

O `Dockerfile` será responsável por definir a imagem da aplicação, incluindo:

* versão padronizada do Python 3.11;
* dependências Python;
* código da aplicação;
* configurações necessárias para execução do serviço.

O `docker-compose.yml` será responsável por fornecer os comandos e serviços necessários para:

* executar a API localmente;
* executar a suíte completa de testes;
* reproduzir o ambiente utilizado pelo restante da equipe.

As versões das dependências Python deverão ser declaradas de forma reproduzível em:

```text
requirements.txt
```

Sempre que possível, as dependências utilizadas pela aplicação e pelos testes deverão possuir versões explicitamente definidas.

A execução padrão da aplicação será:

```bash
docker compose up --build
```

A execução padrão do Test Harness será:

```bash
docker compose run --rm test
```

O uso de ambiente virtual Python (`venv`) continuará sendo permitido para desenvolvimento local, mas o ambiente Docker será considerado a referência oficial para validação da entrega.

## Alternativas Consideradas

### Apenas `venv` + `requirements.txt`

A utilização de um ambiente virtual Python seria suficiente para isolar as dependências Python da aplicação.

Exemplo:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Essa abordagem é mais simples e possui menor custo de inicialização.

Entretanto, ela não padroniza completamente:

* a versão do interpretador Python instalado na máquina;
* bibliotecas do sistema operacional;
* comportamento específico do sistema operacional;
* ferramentas externas disponíveis;
* configuração geral do ambiente.

Como a equipe trabalha em máquinas diferentes, essas diferenças poderiam dificultar a reprodução de problemas e resultados.

Por esse motivo, `venv` será mantido como alternativa de conveniência para desenvolvimento, mas não como ambiente oficial da entrega.

### Poetry ou Pipenv

Ferramentas como Poetry e Pipenv oferecem gerenciamento de ambientes e resolução de dependências com arquivos de lock.

Essas soluções poderiam melhorar o controle de dependências, porém adicionariam uma nova ferramenta ao fluxo do projeto.

Considerando:

* o prazo reduzido do Bootcamp;
* o tamanho atual do projeto;
* a familiaridade da equipe com `pip`;
* o uso de Docker para padronizar o ambiente;

a combinação:

```text
pip + requirements.txt + Docker
```

foi considerada suficiente para esta versão.

A adoção futura de outra ferramenta de gerenciamento de dependências poderá ser reavaliada caso o projeto aumente de complexidade.

### Execução diretamente na máquina do desenvolvedor

Também seria possível instalar Python e todas as dependências diretamente no sistema operacional de cada membro.

Essa alternativa foi rejeitada como padrão por aumentar o risco de:

* conflito entre versões de dependências;
* diferenças entre sistemas operacionais;
* dificuldade de limpeza do ambiente;
* comportamento diferente entre máquinas;
* dificuldade de reproduzir falhas observadas por outro integrante.

## Consequências

### Positivas

* Todos os membros da equipe podem utilizar a mesma versão do Python e o mesmo conjunto de dependências.

* A aplicação pode ser executada sem necessidade de instalar Python diretamente na máquina hospedeira, desde que Docker esteja disponível.

* O ambiente utilizado pelo professor ou por outro avaliador pode reproduzir de forma mais próxima o ambiente utilizado pela equipe.

* O Test Harness pode ser executado em um ambiente padronizado com:

```bash
docker compose run --rm test
```

* As evidências de execução dos testes podem ser produzidas utilizando o mesmo ambiente em diferentes máquinas, reforçando o requisito de observabilidade e reprodutibilidade definido em `docs/SDD.md`.

* Problemas decorrentes de diferenças entre versões locais do Python são reduzidos.

* A configuração necessária para executar o projeto fica versionada junto ao código.

* A aplicação pode ser inicializada por meio de um conjunto pequeno e documentado de comandos.

### Negativas / Limitações

* Docker passa a ser uma dependência necessária para utilizar o ambiente oficial do projeto.

* A primeira construção da imagem pode exigir mais tempo devido ao download da imagem base e instalação das dependências.

* Alterações no `Dockerfile`, nas dependências ou no código podem exigir reconstrução da imagem.

* Docker reduz diferenças entre ambientes, mas não garante reprodutibilidade absoluta entre todas as arquiteturas de hardware e versões do próprio Docker.

* Desenvolvedores que optarem por executar o projeto sem Docker deverão garantir manualmente compatibilidade com a versão de Python e dependências definidas pelo projeto.

* O ambiente Docker deve ser mantido atualizado junto com a aplicação para evitar divergência entre o código e a configuração de execução.

## Regras de versionamento do ambiente

A imagem da aplicação deverá utilizar explicitamente uma versão compatível com Python 3.11, conforme definido na ADR-0001.

Evite utilizar imagens base genéricas que possam mudar de versão de forma inesperada.

As dependências Python devem ser mantidas em:

```text
requirements.txt
```

Mudanças de dependências devem ser versionadas no mesmo fluxo de desenvolvimento que o código que depende delas.

O repositório também deve manter um arquivo:

```text
.dockerignore
```

para impedir a inclusão desnecessária de arquivos locais na imagem, como:

```text
.git/
.venv/
__pycache__/
.pytest_cache/
coverage/
logs/
```

ou outros artefatos que não façam parte da aplicação.

## Relação com o Test Harness

O ambiente Docker deve permitir que a suíte automatizada seja executada sem etapas manuais adicionais além da construção da imagem quando necessária.

O comando:

```bash
docker compose run --rm test
```

deve:

1. inicializar o ambiente necessário para os testes;
2. executar a suíte automatizada;
3. produzir o código de saída correspondente ao resultado dos testes;
4. gerar as evidências previstas no SDD, como logs ou relatórios persistidos.

O comportamento da suíte não deve depender de ferramentas instaladas diretamente na máquina hospedeira além do Docker e de seus componentes necessários.

## Relação com a arquitetura stateless

Como definido na ADR-0003, o PhishGuard não depende de banco de dados nesta versão.

Consequentemente, o ambiente Docker não precisa incluir serviços adicionais como:

```text
PostgreSQL
Redis
MongoDB
```

O ambiente inicial permanece composto essencialmente pela aplicação e pela configuração necessária para execução dos testes.

Isso reduz a quantidade de componentes do `docker-compose.yml` e facilita a reprodução do ambiente.

## Evolução da decisão

Esta decisão deverá ser revisada caso o projeto passe a exigir:

* múltiplos serviços de infraestrutura;
* banco de dados;
* filas ou mensageria;
* ambientes distintos de desenvolvimento e produção;
* pipelines de CI/CD mais complexos;
* gerenciamento avançado de dependências;
* suporte oficial a múltiplas arquiteturas;
* publicação automatizada de imagens.

Mudanças relevantes na estratégia de empacotamento ou execução deverão ser registradas em uma nova ADR ou em uma revisão formal desta decisão.

Até que isso ocorra, **Docker + Docker Compose + `requirements.txt`** permanecem como a estratégia oficial de padronização e reprodução do ambiente do PhishGuard.
