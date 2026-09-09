# Contexto do Projeto para Agentes de IA (Claude Code)

Este arquivo é lido pelo Claude Code e também serve como referência para qualquer pessoa que trabalhe neste repositório.

Ele define o contexto técnico do projeto, as convenções de implementação e as regras do fluxo de trabalho.

Mantenha este arquivo atualizado. Ele faz parte da entrega avaliada no critério **"Contexto & Regras"** da Entrega 1 do Bootcamp III.

---

## O que é este projeto

**PhishGuard** é um serviço HTTP desenvolvido em Python com FastAPI que recebe uma URL e retorna:

* uma pontuação de risco (`score`) entre 0 e 100;
* uma classificação:

  * `segura`;
  * `suspeita`;
  * `perigosa`;
* os motivos (`reasons`) que justificam a pontuação atribuída.

O endpoint principal da aplicação é:

```http
POST /api/v1/analyze
```

A especificação técnica completa está localizada em:

```text
docs/SDD.md
```

O arquivo `docs/SDD.md` é a **fonte da verdade** para requisitos funcionais, requisitos não funcionais, regras de negócio, contratos da API, critérios de pontuação e casos de teste.

Caso exista divergência entre código, teste e especificação, a especificação deve ser revisada antes de alterar o comportamento da aplicação.

---

## Fluxo obrigatório: Spec-Driven Development (SDD)

**Nunca implemente ou altere comportamento sem primeiro refletir a mudança na especificação.**

A ordem de trabalho para qualquer alteração deve ser:

### 1. Especificar primeiro

Se a tarefa introduzir ou modificar:

* requisito funcional;
* requisito não funcional;
* regra de negócio;
* contrato HTTP;
* campo de request ou response;
* heurística;
* critério de normalização;
* pontuação;
* limiar de classificação;
* comportamento de validação;

atualize primeiro:

```text
docs/SDD.md
```

Se a alteração surgir devido a feedback do grupo, comportamento observado nos testes ou refinamento da implementação, registre também a mudança na seção **"Refinamento por Feedback"** ou no histórico correspondente do SDD, incluindo data e motivo.

Não dependa apenas do número da seção, pois a estrutura do documento pode evoluir.

### 2. Decompor em unidades isoladas

Siga a arquitetura definida no SDD:

```text
api.py
models.py
url_normalizer.py
scorer.py
blocklist.py
heuristics/*.py
```

Cada heurística deve possuir responsabilidade única.

Uma nova heurística deve ser implementada em um novo arquivo dentro de:

```text
src/phishguard/heuristics/
```

Não implemente regras específicas de heurística diretamente em `scorer.py`.

O `scorer.py` deve atuar principalmente como orquestrador das regras existentes.

### 3. Escrever os testes antes ou junto da implementação

Toda nova heurística ou regra deve possuir, no mínimo:

1. um caso positivo, no qual a regra dispara;
2. um caso negativo, no qual a regra não dispara;
3. um caso de borda (*edge case*).

Sempre que possível, escreva o teste antes da implementação.

Os testes devem validar o comportamento definido no SDD, e não apenas reproduzir o comportamento atual do código.

### 4. Rodar a suíte completa

Antes de abrir um Pull Request, execute a suíte completa de testes.

Com o ambiente local:

```bash
./scripts/run_harness.sh
```

Ou utilizando Docker:

```bash
docker compose run --rm test
```

Nunca abra Pull Request com testes quebrando.

### 5. Fazer commits pequenos e descritivos

Utilize commits em português no padrão:

```text
tipo: descrição curta
```

Exemplos:

```text
feat: adiciona heuristica de tld suspeito
test: adiciona casos de borda para ip literal
fix: corrige normalizacao de host unicode
docs: atualiza especificacao da rn-06
refactor: separa regras de pontuacao do scorer
chore: ajusta configuracao do ambiente docker
```

Evite commits genéricos como:

```text
update
alteracoes
ajustes
final
teste
```

---

## Convenções de código

### Linguagem e framework

* Python 3.11.
* FastAPI como camada HTTP.
* Pydantic para validação e contratos de dados.
* Formatação com `black`.
* Imports organizados na ordem:

  1. biblioteca padrão;
  2. dependências de terceiros;
  3. módulos locais.

---

## Estrutura das heurísticas

Cada heurística deve ser implementada como uma **função pura**.

Contrato esperado:

```python
def check(parsed: ParsedURL) -> HeuristicResult:
    ...
```

Uma heurística:

* recebe somente os dados necessários para análise;
* não altera estado externo;
* não realiza escrita em arquivos;
* não acessa banco de dados;
* não faz chamadas HTTP;
* não executa consultas externas;
* não depende da hora atual;
* produz sempre o mesmo resultado para a mesma entrada.

Essa característica é essencial para que o Test Harness seja determinístico e confiável.

Cada heurística deve disparar **no máximo uma vez por análise**, mesmo que múltiplas ocorrências do mesmo padrão estejam presentes na URL.

---

## Determinismo

Para a mesma URL, utilizando:

* a mesma versão do código;
* as mesmas listas locais;
* as mesmas configurações;
* os mesmos pesos;

o resultado da análise deve ser sempre o mesmo.

Isso inclui:

* `normalized_host`;
* `score`;
* `classification`;
* conteúdo de `reasons`;
* ordem dos itens de `reasons`.

A lista de motivos não deve depender de estruturas sem ordenação previsível.

Não introduza campos variáveis, como timestamps gerados durante a análise, no resultado determinístico sem que isso esteja explicitamente previsto no SDD.

---

## Comparações de texto

Comparações relacionadas às regras de negócio devem respeitar o comportamento definido na especificação.

Quando aplicável, comparações devem ser **case-insensitive**.

Exemplo:

```text
login
Login
LOGIN
```

devem ser tratados de forma equivalente quando a regra correspondente determinar busca sem diferenciação entre maiúsculas e minúsculas.

Não altere regras de normalização sem atualizar previamente o SDD.

---

## Constantes de negócio

Constantes relacionadas às regras de negócio devem permanecer centralizadas em:

```text
src/phishguard/config.py
```

Exemplos:

* pesos das heurísticas;
* limiares de classificação;
* TLDs suspeitos;
* encurtadores conhecidos;
* marcas monitoradas;
* domínios oficiais;
* palavras-chave sensíveis;
* demais listas utilizadas pelas regras.

Não replique essas constantes dentro de arquivos de heurísticas.

Evite valores de negócio *hardcoded* em múltiplos pontos da aplicação.

---

## Pontuação e classificação

A pontuação deve seguir exclusivamente os critérios definidos no SDD e nas constantes correspondentes.

O score final deve permanecer no intervalo:

```text
0–100
```

A classificação deve utilizar exatamente os valores definidos pelo contrato:

```text
segura
suspeita
perigosa
```

Não utilize variações como:

```text
seguro
suspeito
perigoso
safe
dangerous
```

quando estiver produzindo a resposta oficial da API.

Alterações nos pesos das heurísticas ou nos limiares de classificação são decisões de produto e não devem ser realizadas pelo agente sem confirmação humana e atualização prévia do SDD.

---

## Allowlist e blocklist

As listas locais devem ser tratadas conforme as regras definidas no SDD.

A `allowlist` possui prioridade sobre a análise heurística e deve impedir falsos positivos para domínios explicitamente confiáveis.

A `blocklist` força o comportamento definido pela regra correspondente.

As verificações devem utilizar o domínio após a normalização especificada no SDD.

Não altere a precedência entre `allowlist`, `blocklist` e heurísticas sem:

1. confirmação humana;
2. atualização prévia da especificação;
3. atualização dos testes correspondentes.

---

## Normalização de URLs

A normalização deve ser realizada exclusivamente pelo componente:

```text
url_normalizer.py
```

Esse componente é responsável por:

* validar a entrada;
* validar o esquema;
* extrair o host;
* normalizar o host;
* extrair o path;
* extrair a query;
* lidar com URLs Unicode/IDN conforme definido na especificação.

As heurísticas não devem implementar parsers próprios de URL.

Depois que uma URL for normalizada, as heurísticas devem trabalhar sobre a representação estruturada fornecida pelo normalizador.

---

## Tratamento de erros

Entradas inválidas devem resultar em:

```python
InvalidURLError
```

Não deixe exceções genéricas de parsing ou validação vazarem até a camada HTTP.

A camada da API deve converter os erros de validação previstos para resposta HTTP:

```http
422 Unprocessable Entity
```

Não classifique uma URL inválida como `segura` por padrão.

Não utilize `400` para casos que o contrato atual do SDD define como `422`.

---

## Contratos HTTP

O endpoint principal é:

```http
POST /api/v1/analyze
```

O endpoint de disponibilidade é:

```http
GET /health
```

Os contratos de entrada e saída devem utilizar JSON.

Qualquer alteração em:

* endpoint;
* método HTTP;
* nome de campo;
* tipo de campo;
* campo obrigatório;
* formato de erro;
* valor de classificação;
* estrutura de `reasons`;

exige atualização prévia de:

```text
docs/SDD.md
```

Os modelos Pydantic devem refletir os contratos documentados no SDD.

---

## Ausência de dependências externas

Nenhuma heurística deve consultar serviços externos nesta versão.

Não utilize serviços como:

* Google Safe Browsing;
* VirusTotal;
* APIs externas de reputação;
* consultas DNS remotas;
* serviços externos de threat intelligence.

A análise desta entrega deve ser local, determinística e executada em memória.

Consulte as ADRs vigentes antes de propor mudanças arquiteturais relacionadas a serviços externos ou persistência.

---

## Testes

Os testes devem ser organizados de forma a permitir validação independente das unidades.

Sempre que aplicável, devem existir testes para:

* normalização;
* cada heurística individual;
* `allowlist`;
* `blocklist`;
* `scorer`;
* contratos Pydantic;
* endpoint `/api/v1/analyze`;
* endpoint `/health`;
* entradas inválidas;
* casos de borda;
* determinismo.

Utilize `pytest` como ferramenta principal para execução da suíte.

Não faça testes dependentes de:

* internet;
* horário atual;
* ordem imprevisível de estruturas de dados;
* estado de máquina;
* arquivos externos não versionados;
* serviços externos.

O resultado da suíte deve ser reproduzível.

---

## Decomposição do sistema

A arquitetura esperada segue, de forma simplificada, este fluxo:

```text
HTTP Request
     │
     ▼
   api.py
     │
     ▼
 models.py
     │
     ▼
scorer.py
     │
     ├── url_normalizer.py
     │
     ├── heuristics/*.py
     │
     └── blocklist.py
     │
     ▼
 models.py
     │
     ▼
HTTP Response
```

Responsabilidades:

### `api.py`

Responsável por:

* endpoints FastAPI;
* recebimento das requisições;
* tratamento de erros HTTP;
* serialização da resposta.

Não deve conter regras de negócio de phishing.

### `models.py`

Responsável pelos modelos Pydantic dos contratos de entrada e saída.

### `url_normalizer.py`

Responsável por parsing, normalização e validação da URL.

### `heuristics/*.py`

Cada arquivo implementa uma única heurística de risco.

### `blocklist.py`

Responsável pelas verificações das listas locais de domínios confiáveis e bloqueados.

### `scorer.py`

Responsável por:

* orquestrar a análise;
* executar as heurísticas;
* aplicar regras de precedência;
* agregar os pontos;
* limitar o score ao intervalo válido;
* determinar a classificação;
* montar o resultado final.

Não deve concentrar implementações específicas das heurísticas.

---

## Branches e Pull Requests

### `main`

Branch estável e protegida.

**É proibido fazer commit direto em `main`.**

### `develop`

Branch de integração do time.

### `feature/<nome-curto>`

Uma branch por unidade de trabalho.

Exemplos:

```text
feature/heuristica-ip-literal
feature/heuristica-tld-suspeito
feature/api-endpoint-analyze
feature/url-normalizer
```

Branches `feature/*` devem partir de `develop`.

O fluxo esperado é:

```text
develop
   │
   └── feature/<nome>
          │
          └── Pull Request → develop
```

---

## Requisitos para Pull Request

Todo Pull Request deve:

1. identificar qual requisito, regra ou seção da especificação está sendo implementada;
2. explicar brevemente a alteração;
3. informar que a suíte de testes foi executada;
4. estar com todos os testes passando;
5. possuir pelo menos uma aprovação de outro membro do time antes do merge.

Consulte também:

```text
GITHUB_SETUP.md
.github/PULL_REQUEST_TEMPLATE.md
```

Não abra PR diretamente para `main`, salvo se o fluxo do grupo for explicitamente alterado e documentado.

---

## Como rodar o projeto

### Com Docker

Subir a API:

```bash
docker compose up --build
```

A API ficará disponível em:

```text
http://localhost:8000
```

Executar a suíte completa:

```bash
docker compose run --rm test
```

---

## Como rodar sem Docker

Criar o ambiente virtual:

```bash
python -m venv .venv
```

Ativar no Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar as dependências:

```bash
pip install -r requirements.txt
```

Subir a API:

```bash
uvicorn phishguard.api:app --reload
```

Executar o Test Harness:

```bash
./scripts/run_harness.sh
```

---

## Exemplos de tarefas para agentes de IA

### Implementar uma heurística

```text
Implemente a heurística RF-08 (TLD suspeito) em
src/phishguard/heuristics/suspicious_tld.py seguindo o contrato de
HeuristicResult e adicione os testes correspondentes.
```

### Adicionar um caso de borda

```text
Adicione um caso de borda para URL com host IPv6 e atualize a
especificação caso o comportamento ainda não esteja documentado.
```

### Revisar uma implementação

```text
Revise scorer.py contra as regras de negócio vigentes em docs/SDD.md
e aponte divergências entre implementação, testes e especificação.
```

### Verificar contrato da API

```text
Compare os modelos Pydantic e o endpoint POST /api/v1/analyze com os
contratos definidos em docs/SDD.md e identifique inconsistências.
```

### Criar testes

```text
Crie testes positivo, negativo e de borda para a heurística de
detecção de encurtadores, respeitando as regras definidas no SDD.
```

---

## O que o agente NÃO deve fazer sem confirmação humana

O agente não deve, por iniciativa própria:

* alterar os limiares de classificação;
* alterar os pesos das heurísticas;
* alterar a precedência entre `allowlist`, `blocklist` e análise heurística;
* adicionar dependência de rede;
* integrar serviços externos;
* adicionar persistência em banco de dados;
* modificar contratos HTTP;
* adicionar ou remover campos do JSON oficial da API;
* alterar regras de normalização;
* adicionar novas palavras-chave, TLDs ou marcas monitoradas como decisão de produto;
* alterar requisitos ou regras de negócio apenas para fazer um teste passar;
* fazer commit direto em `main`;
* remover testes existentes sem justificativa;
* ignorar divergências entre código e especificação.

Quando uma dessas mudanças parecer necessária, o agente deve apresentar a divergência e aguardar uma decisão humana antes de alterar o comportamento especificado.

---

## Prioridade das fontes

Ao trabalhar no repositório, utilize a seguinte ordem de prioridade:

1. `docs/SDD.md` — requisitos, regras de negócio e contratos;
2. ADRs vigentes — decisões arquiteturais;
3. este `CLAUDE.md` — processo e convenções de trabalho;
4. testes automatizados;
5. implementação atual.

Se um teste ou implementação contradizer explicitamente o SDD, não trate automaticamente o código atual como correto.

Identifique a divergência antes de modificar o comportamento.

---

## Regra principal

> **Especificar → Testar → Implementar → Validar → Revisar**

O objetivo do projeto não é apenas produzir uma API funcional, mas demonstrar um processo de desenvolvimento orientado por especificação, com requisitos rastreáveis, unidades testáveis e comportamento reproduzível.
