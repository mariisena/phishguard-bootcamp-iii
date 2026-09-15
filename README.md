# PhishGuard

> Serviço de detecção de URLs suspeitas e de phishing via API HTTP.

**Bootcamp III — Turma B-0726 | Entrega 1**

---

## Visão Geral

O **PhishGuard** é uma API HTTP desenvolvida em Python que recebe uma URL e retorna uma avaliação de risco estruturada. O objetivo é identificar, de forma local e determinística, padrões estruturais associados a ataques de phishing — sem depender de serviços externos.

### Problema que resolve

Ataques de phishing frequentemente utilizam URLs com padrões reconhecíveis: endereço IP no lugar de domínio, caractere `@` para ocultar o host real, domínios que imitam marcas conhecidas, TLDs suspeitos, entre outros. O PhishGuard aplica um conjunto de heurísticas sobre a estrutura da URL e retorna uma pontuação de risco (0–100), uma classificação categórica e os motivos que justificam o resultado.

### O que o serviço entrega

Para cada URL analisada, a resposta contém:

| Campo | Descrição |
|---|---|
| `score` | Pontuação de risco de 0 a 100 |
| `classification` | `segura` (0–29), `suspeita` (30–59) ou `perigosa` (60–100) |
| `reasons` | Lista ordenada e determinística dos sinais de risco identificados |
| `normalized_host` | Host canônico em minúsculas, sem porta e em formato IDNA ASCII |

### Heurísticas implementadas

| Heurística | Sinal detectado | Pontos |
|---|---|:---:|
| IP como host | Host é um endereço IPv4 ou IPv6 | 25 |
| Uso de `@` | Caractere `@` na seção de autoridade da URL | 25 |
| Excesso de subdomínios | Mais de 3 subdomínios além do domínio base | 15 |
| TLD suspeito | TLD pertencente à lista fechada definida na spec | 15 |
| Encurtador conhecido | Host pertence à lista de encurtadores monitorados | 15 |
| Impersonação de marca | Host contém nome de marca monitorada fora do domínio oficial | 25 |
| Punycode / Unicode | Host em punycode (`xn--`) ou com caracteres não ASCII | 25 |
| Ausência de HTTPS | Esquema da URL é `http` | 10 |
| URL muito longa | URL com mais de 75 caracteres | 10 |
| Palavra-chave sensível | Palavra sensível no path/query **e** ao menos outro sinal ativo | 20 |

### Fora de escopo (nesta versão)

- Consulta a serviços externos de reputação (Google Safe Browsing, VirusTotal etc.)
- Persistência em banco de dados
- Autenticação/autorização de consumidores
- Interface gráfica
- Rastreamento de redirecionamentos de URLs encurtadas

---

## Guia de Instalação e Execução

### Pré-requisitos

- **Docker** e **Docker Compose** (recomendado — garante reprodutibilidade) **ou**
- **Python 3.11+** com `pip`

---

### Opção 1 — Com Docker (recomendado)

**Subir a API:**

```bash
docker compose up --build
```

A API ficará disponível em `http://localhost:8000`.

**Executar a suíte de testes:**

```bash
docker compose run --rm test
```

---

### Opção 2 — Sem Docker (ambiente local)

**1. Clone o repositório:**

```bash
git clone https://github.com/<seu-usuario>/phishguard-bootcamp-iii.git
cd phishguard-bootcamp-iii
```

**2. Crie e ative o ambiente virtual:**

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

**3. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**4. Execute a suíte de testes:**

```bash
python -m pytest tests/ -v
```

---

### Endpoints disponíveis

**`POST /api/v1/analyze`** — Analisa uma URL e retorna a avaliação de risco.

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "http://192.168.0.1/login"}'
```

Exemplo de resposta:

```json
{
  "url": "http://192.168.0.1/login",
  "normalized_host": "192.168.0.1",
  "score": 45,
  "classification": "suspeita",
  "reasons": ["host_ip", "palavra_chave_sensivel_no_path_query"]
}
```

**`GET /health`** — Verifica a disponibilidade do serviço.

```bash
curl http://localhost:8000/health
```

---

## ADRs — Decisões Arquiteturais

As decisões técnicas estruturais do projeto estão documentadas na pasta [`docs/adr/`](docs/adr/). Abaixo um registro sintético de cada decisão.

---

### ADR-0001 — Python 3.11 + FastAPI + Pydantic

**Status:** Aceita

**Decisão:** Utilizar Python 3.11 como linguagem principal, FastAPI como framework HTTP e Pydantic para validação dos contratos de entrada e saída.

**Por quê:**
- A equipe possui maior familiaridade com Python do que com as alternativas (Node.js/Express).
- FastAPI gera documentação OpenAPI automaticamente a partir dos modelos, reduzindo divergência entre código e contrato.
- Pydantic garante validação estruturada dos payloads JSON com pouco código adicional.
- Flask e Django foram descartados: Flask exigiria mais código para validação de contratos; Django inclui recursos (ORM, admin) além do necessário para um serviço stateless.
- pytest integra-se nativamente com o ecossistema Python, simplificando testes unitários e de integração.

---

### ADR-0002 — Motor de regras heurísticas (sem Machine Learning)

**Status:** Aceita

**Decisão:** Detectar phishing exclusivamente por meio de regras heurísticas explícitas, determinísticas e explicáveis. Machine Learning e serviços externos de reputação estão fora de escopo nesta versão.

**Por quê:**
- O projeto segue **Spec-Driven Development (SDD)**: o comportamento esperado deve ser definido em especificação e validado por testes automatizados. Regras heurísticas permitem rastreabilidade direta entre `Requisito → Regra → Implementação → Teste → Motivo da resposta`.
- ML exigiria dataset rotulado, pipeline de treinamento, versionamento de modelo e critérios para testar decisões — custo fora do escopo da Entrega 1.
- Serviços externos introduziriam dependência de rede, variação de resultados ao longo do tempo e maior complexidade nos testes determinísticos.
- Cada heurística é uma função pura, isolada e testável individualmente — propriedade essencial para um Test Harness confiável.

---

### ADR-0003 — Serviço stateless, sem banco de dados

**Status:** Aceita

**Decisão:** O PhishGuard não utiliza banco de dados. As listas de domínios (`allowlist` e `blocklist`) são armazenadas em arquivos JSON locais (`data/allowlist.json` e `data/blocklist.json`), carregados em memória na inicialização do serviço.

**Por quê:**
- O volume de dados (listas pequenas e controladas) não justifica a complexidade de PostgreSQL, Redis ou outro serviço externo.
- Eliminar banco de dados simplifica o ambiente Docker, o Test Harness e a reprodutibilidade: sem migrations, sem fixtures de banco, sem dependências de conexão.
- O resultado da análise não depende de requisições anteriores — duas chamadas idênticas retornam o mesmo resultado (determinismo).
- Adoção futura de banco de dados deverá ser registrada em nova ADR, considerando impactos em arquitetura, testes e desempenho.

---

### ADR-0004 — Docker e Docker Compose para padronização do ambiente

**Status:** Aceita

**Decisão:** Usar Docker e Docker Compose como forma padrão de execução da API e da suíte de testes, garantindo reprodutibilidade independentemente do sistema operacional ou configuração local de cada desenvolvedor.

**Por quê:**
- A equipe trabalha em máquinas com sistemas operacionais e configurações distintas.
- Docker elimina diferenças de versão do Python, bibliotecas e variáveis de ambiente entre ambientes.
- `docker compose run --rm test` permite executar o Test Harness de forma padronizada e reproduzível.
- A execução local sem Docker também é suportada como alternativa, desde que o Python 3.11 e as dependências do `requirements.txt` estejam disponíveis.

---

### ADR-0005 — Uso de agente de IA (Claude Code / Antigravity) no desenvolvimento

**Status:** Aceita

**Decisão:** Adotar agente de IA como ferramenta auxiliar no fluxo de desenvolvimento, operando estritamente dentro das diretrizes do `CLAUDE.md` e do SDD.

**Por quê:**
- O agente acelera a geração de código estruturado (heurísticas, testes, documentação) respeitando os contratos definidos na especificação.
- A adoção é condicionada ao fluxo **Especificar → Testar → Implementar → Validar**: o agente não deve alterar pesos, contratos ou regras de negócio sem aprovação humana explícita.
- Qualquer divergência identificada entre código, testes e SDD deve ser reportada ao time antes de ser resolvida.

---

## Estrutura do Projeto

```text
phishguard-bootcamp-iii/
├── analyzer/
│   ├── config.py           # Constantes normativas (pesos, listas, limiares)
│   ├── models.py           # Schemas Pydantic de request/response
│   ├── scorer.py           # Motor de orquestração e pontuação
│   ├── url_normalizer.py   # Validação e normalização da URL
│   ├── blocklist.py        # Consulta a allowlist e blocklist locais
│   └── rules/              # Uma heurística por arquivo (funções puras)
├── data/
│   ├── allowlist.json
│   └── blocklist.json
├── docs/
│   ├── SDD.md              # Especificação técnica (fonte da verdade)
│   └── adr/                # Decisões arquiteturais (ADR-0001 a ADR-0005)
├── tests/                  # Suíte de testes (pytest)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── CLAUDE.md               # Diretrizes para agentes de IA e convenções do projeto
```

---

## Documentação Completa

- **Especificação técnica:** [`docs/SDD.md`](docs/SDD.md)
- **Decisões arquiteturais:** [`docs/adr/`](docs/adr/)
- **Diretrizes para agentes de IA:** [`CLAUDE.md`](CLAUDE.md)
