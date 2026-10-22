# Especificação Técnica — Spec-Driven Development (SDD)

**Projeto:** PhishGuard — Detector de URLs Suspeitas/Phishing
**Disciplina:** Bootcamp III — Turma B-0726
**Entrega:** 1 — Ambiente, Especificação Técnica e Test Harness / 2 — Publicação, Refinamento e Análise Crítica / 3 — Etapa Final
**Metodologia:** Spec-Driven Development (SDD)
**Status:** **As-Built** — reflete o código entregue na release `v3.0.0`
**Versão do documento:** 3.0
**Última atualização:** 2026-10-20 (ver seção 9, Histórico de Versões)

---

## 1. Descrição do Problema

Phishing é uma das formas mais comuns de fraude digital: um atacante cria ou distribui uma URL que imita um site legítimo (bancos, e-mail, redes sociais, serviços de pagamento) para induzir a vítima a fornecer credenciais, dados pessoais ou financeiros. Grande parte dessas URLs apresenta padrões estruturais reconhecíveis — mesmo sem consultar bases externas em tempo real — como uso de IP no lugar de domínio, presença do caractere `@`, domínios com aparência de marcas conhecidas, uso de encurtadores, excesso de subdomínios ou caracteres unicode que imitam letras latinas (homograph/punycode).

O **PhishGuard** é um serviço (API HTTP) que recebe uma URL e retorna uma avaliação de risco (pontuação de 0 a 100 e uma classificação categórica), explicando quais sinais de risco foram identificados.

Na Entrega 1, este documento especificou o problema, decompôs a solução em unidades testáveis e definiu o *harness* de testes, com uma implementação de referência como prova de conceito. Nas Entregas 2 e 3 a especificação foi refinada a partir dos testes e das revisões do grupo (seção 8). **Esta versão é a As-Built:** requisitos, regras, contratos e componentes descritos aqui correspondem ao código da release `v3.0.0`, e cada regra é validada pelo Test Harness (seção 7).

### 1.1 Fora de escopo (na versão 3.0.0)

- Consulta a serviços externos de reputação de URL (Google Safe Browsing, VirusTotal etc.) — candidato a evolução futura (ver ADR-0002).
- Persistência em banco de dados — o serviço é *stateless* nesta versão (ver ADR-0003).
- Autenticação/autorização de usuários da API.
- Interface gráfica (o consumo é via API HTTP; a suíte de testes cobre o contrato da API).
- Resolução ou acompanhamento de redirecionamentos de URLs encurtadas.
- Detecção avançada de typosquatting por distância de edição, modelos de linguagem ou aprendizado de máquina. Nesta versão, a regra de marca cobre impersonação por inclusão do nome da marca no host.
- Uso de Public Suffix List externa; a regra de subdomínios utiliza uma aproximação determinística definida na seção 4.2.

---

## 2. Requisitos Funcionais (RF)

| ID | Requisito |
| ---- | ----------- |
| **RF-01** | O sistema deve receber uma URL (string) via `POST /api/v1/analyze` e retornar uma pontuação de risco de 0 a 100. |
| **RF-02** | O sistema deve classificar a URL em `segura` (0–29), `suspeita` (30–59) ou `perigosa` (60–100). |
| **RF-03** | O sistema deve retornar uma lista ordenada de motivos que justifique a pontuação ou eventual sobreposição por lista local. |
| **RF-04** | O sistema deve normalizar e validar a entrada antes da análise, aceitando apenas URLs HTTP(S) absolutas com host válido. |
| **RF-05** | O sistema deve identificar quando o host é um endereço IP IPv4 ou IPv6 em vez de um nome de domínio. |
| **RF-06** | O sistema deve identificar uso do caractere @ na seção de autoridade/userinfo da URL, sinal associado à ocultação do host real. |
| **RF-07** | O sistema deve identificar excesso de subdomínios conforme a regra operacional definida na seção 4.2. |
| **RF-08** | O sistema deve identificar TLDs da lista fechada de TLDs suspeitos definida nesta especificação. |
| **RF-09** | O sistema deve identificar domínios pertencentes à lista fechada de encurtadores conhecidos. A correspondência é por igualdade exata OU por sufixo com fronteira de ponto: o host dispara se `host == encurtador` ou se `host` termina em `"." + encurtador`. Assim, ``www.`bit.ly` e `m.bit.ly` disparam, mas `notbit.ly` (sem ponto de fronteira) e `bit.ly.evil.com` (encurtador no meio do host, não no final) não disparam. |
| **RF-10** | O sistema deve identificar possível impersonação de marcas monitoradas quando o host contiver o nome da marca, mas não pertencer ao domínio oficial cadastrado para essa marca. |
| **RF-11** | O sistema deve identificar hosts em Punycode (xn--) ou hosts originalmente informados com caracteres não ASCII/Unicode. |
| **RF-12** | O sistema deve identificar ausência de HTTPS quando o esquema da URL for http. |
| **RF-13** | O sistema deve identificar URLs anormalmente longas (mais de 75 caracteres). |
| **RF-14** | O sistema deve identificar palavras-chave sensíveis no path ou query, de forma case-insensitive, e pontuá-las apenas quando ao menos outra heurística RF-05 a RF-13 tiver disparado. |
| **RF-15** | O sistema deve checar allowlist e blocklist locais por correspondência exata do host canônico; allowlist e blocklist sobrepõem o resultado heurístico conforme as regras de negócio. |
| **RF-16** | O sistema deve expor GET /health e retornar um JSON de disponibilidade, conforme o contrato da seção 5.5. |
| **RF-17** | Entradas ausentes, nulas, vazias, de tipo incorreto, fora do limite de tamanho ou URLs inválidas devem retornar HTTP 422 com mensagem descritiva, sem exceção não tratada. |

---

## 3. Requisitos Não-Funcionais (RNF)

| ID | Requisito | Descrição |
| ---- | ----------- | ----------- |
| **RNF-01** | **Desempenho** | Cada análise deve ser concluída em até 300 ms em ambiente de desenvolvimento padrão, sem chamadas de rede a terceiros e com processamento predominantemente em memória. |
| **RNF-02** | **Determinismo** | Para a mesma entrada e a mesma versão de configuração/listas, url, normalized_host, score, classification e reasons devem ser idênticos. A ordem de reasons também é determinística. |
| **RNF-03** | **Testabilidade** | Cada heurística deve ser uma função pura testável isoladamente da camada HTTP e das demais heurísticas. |
| **RNF-04** | **Extensibilidade** | Novas heurísticas devem poder ser adicionadas por meio da mesma interface de entrada/saída, sem alterar o contrato das heurísticas existentes. |
| **RNF-05** | **Portabilidade** | O serviço deve executar de forma reproduzível por docker compose up, sem configuração manual específica do ambiente do desenvolvedor além de Docker/Compose. A suíte roda no mesmo ambiente por `docker compose run --rm test`. |
| **RNF-06** | **Observabilidade mínima** | Toda execução da suíte deve gerar relatório ou log persistido em arquivo como evidência de execução. |
| **RNF-07** | **Internacionalização de entrada** | O normalizador deve aceitar URLs contendo IDN/Unicode sem lançar exceção não tratada e deve produzir representação canônica determinística. |
| **RNF-08** | **Stack tecnológica** | A aplicação deve ser desenvolvida em Python com FastAPI e schemas Pydantic, visando simplicidade, conteinerização e reprodutibilidade. Versão de referência: Python 3.11 (imagem `python:3.11-slim` e CI), conforme ADR-0001. |
| **RNF-09** | **Contrato JSON** | Os corpos de request e response da API devem utilizar JSON. Respostas de erro previstas também devem ser serializadas em JSON. |
| **RNF-10** | **Modularidade** | O código deve separar claramente camada HTTP, modelos de contrato, normalização, heurísticas, listas locais e agregação/scoring. |

---

## 4. Regras de Negócio (RN)

1. **RN-01 — Pontuação cumulativa e limitada:** Cada heurística disparada soma seus pontos uma única vez. O score heurístico final é limitado ao intervalo [0, 100] por clamp.
2. **RN-02 — Classificação por faixa:** Score de 0 a 29 resulta em segura; 30 a 59 em suspeita; 60 a 100 em perigosa. As faixas são constantes centralizadas e não devem ser repetidas de forma hardcoded.
3. **RN-03 — Allowlist tem prioridade absoluta:** Se o host canônico, sem prefixo ``www.``, corresponder exatamente a um item da allowlist, o resultado final deve ser score 0, classification segura e reasons = ["dominio_allowlist"]. A allowlist é avaliada antes da blocklist.
4. **RN-04 — Blocklist força classificação perigosa:** Se o host canônico, sem prefixo ``www.``, corresponder exatamente a um item da blocklist e não houver correspondência na allowlist, o resultado final deve ser score 100, classification perigosa e reasons = ["dominio_blocklist"].
5. **RN-05 — Impersonação de marca exige ausência de domínio oficial:** A heurística dispara quando o host contém, de forma case-insensitive, o nome de uma marca monitorada e o host não é o domínio oficial nem um subdomínio desse domínio oficial. Antes da comparação, é aplicada uma normalização leet speak básica (0→o, 1→l, 3→e, 4→a, 5→s, 7→t). A heurística representa impersonação por inclusão de marca; typosquatting ortográfico genérico (troca de letras distintas, letras duplicadas, etc.) permanece fora de escopo, sendo coberta apenas essa substituição específica de caracteres leet.
6. **RN-06 — Palavra-chave sensível exige outro sinal:** A presença de palavra-chave sensível no path/query só adiciona pontos se ao menos uma heurística RF-05 a RF-13 também tiver disparado. Múltiplas palavras ou ocorrências não acumulam pontos adicionais.
7. **RN-07 — Uma heurística dispara no máximo uma vez:** Cada categoria de heurística soma pontos no máximo uma vez por análise, ainda que o padrão apareça repetidamente.
8. **RN-08 — Encurtadores são sinalizados, não bloqueados:** Host de encurtador conhecido adiciona pontuação e o motivo encurtador_conhecido_destino_nao_verificado. O serviço não segue o redirecionamento nesta entrega.
9. **RN-09 — Entrada inválida não recebe classificação:** Se a entrada não puder ser validada/normalizada, a API retorna HTTP 422 e não produz score, classification ou reasons de análise.

> Nota: A allowlist e a blocklist não devem conter o mesmo host. O Test Harness deve incluir um teste de consistência de configuração para detectar interseção entre as duas listas. Caso exista interseção por erro de configuração, RN-03 ainda prevalece por definição.

## 4.1. Pontuação normativa e códigos de motivo

| Heurística | Pontos | reason |
| ------------- | :------: | -------- |
| Host é IPv4/IPv6 | 25 | host_ip |
| Uso de @ na autoridade/userinfo | 25 | uso_arroba_userinfo |
| Excesso de subdomínios | 15 | subdominios_excessivos |
| TLD suspeito | 15 | tld_suspeito |
| Encurtador conhecido | 15 | encurtador_conhecido_destino_nao_verificado |
| Possível impersonação de marca | 25 | `possivel_impersonacao_marca:<marca>` |
| Punycode ou host Unicode | 25 | punycode_ou_unicode_suspeito |
| Sem HTTPS | 10 | sem_https |
| URL com mais de 75 caracteres | 10 | url_muito_longa |
| Palavra-chave sensível no path/query, condicionada à RN-06 | 20 | palavra_chave_sensivel_no_path_query |

> Ordem normativa das heurísticas/reasons: host IP → @/userinfo → subdomínios → TLD → encurtador → impersonação → Punycode/Unicode → sem HTTPS → URL longa → palavra-chave sensível. A lista reasons deve respeitar essa ordem para garantir determinismo.

## 4.2. Listas fechadas e critérios operacionais

**TLDs suspeitos**: `.zip`, `.top`, `.xyz`, `.country`, `.click`, `.link`, `.work`, `.gq`, `.tk`, `.ml`, `.cf`, `.mom`, `.fit`
**Encurtadores conhecidos**: `bit.ly`, `tinyurl.com`, `t.co`, `is.gd`, `goo.gl`, `ow.ly`, `buff.ly`, `cutt.ly`, `rebrand.ly`
**Palavras-chave sensíveis**: `login`, `verify`, `secure`, `update`, `confirm`, `account`, `senha`, `banco`, `wp-login`

| Marca monitorada | Domínio oficial |
| ---------------- | --------------- |
| paypal | paypal.com |
| google | google.com |
| microsoft | microsoft.com, live.com, office.com |
| apple | apple.com |
| itau | itau.com.br |
| caixa | caixa.gov.br |
| bradesco | bradesco.com.br |
| nubank | nubank.com.br |
| amazon | amazon.com, amazon.com.br |

**Limitação conhecida da RN-05**: a regra procura o nome da marca por inclusão de substring no host, após a normalização leet básica. Por isso, palavras legítimas que contenham o nome de uma marca podem gerar falso positivo. Por exemplo, `https://capitaurbana.com` dispara para `itau`, e `https://caixadesom.com` dispara para `caixa`. Esse comportamento está dentro do escopo especificado; a detecção avançada de typosquatting continua fora de escopo nesta entrega.

**Critério de subdomínios nesta entrega**: para hosts que não são IP, o hostname é separado por pontos. Para manter a implementação local e determinística sem Public Suffix List, os dois últimos labels são tratados como domínio-base; a heurística dispara quando houver mais de três labels anteriores a esses dois. Portanto, a.b.c.d.example.com dispara (4 subdomínios) e a.b.c.example.com não dispara (3). Essa aproximação é conhecida e poderá ser substituída por uma Public Suffix List em evolução futura.

**Critério de Punycode/Unicode**: a heurística dispara se o host original possuir qualquer caractere não ASCII ou se a forma canônica IDNA contiver label iniciado por xn--. O normalizador deve preservar informação suficiente para essa checagem antes/depois da conversão IDNA.

**Critério do caractere @**: a regra considera @ na seção de autoridade/userinfo, isto é, entre // e o início de path/query/fragmento. Um @ apenas no path/query não deve disparar RF-06.

**Critério de TLD (RF-08)**: o TLD é o último label do host canônico (minúsculas, sem ponto final e em IDNA ASCII), comparado com a lista fechada acima sem o ponto inicial.

**Critério de URL longa (RF-13)**: o comprimento considerado é o da entrada após o trim (o campo `url` da resposta), incluindo esquema, host, path, query e fragmento.

**Critério de palavra-chave (RF-14)**: a busca é por **inclusão de substring** na visão em minúsculas do path e da query (N-08). Por isso `/blogin` contém `login` e `/updates` contém `update`. O fragmento não participa. Esse critério foi mantido por decisão do grupo (Issue #133): o falso positivo da substring é contido pela RN-06, já que a palavra-chave sozinha não pontua.

**Critério de marca com mais de uma ocorrência (RF-10)**: se o host contiver mais de uma marca monitorada, apenas a primeira na ordem da tabela acima é reportada em `possivel_impersonacao_marca:<marca>`, pois a heurística dispara no máximo uma vez (RN-07). A comparação com o domínio oficial usa o host sem a substituição leet.

## 4.3. Listas locais (allowlist e blocklist)

As listas ficam em `data/allowlist.json` e `data/blocklist.json`, cada uma um array JSON de strings, versionadas no repositório (ADR-0003).

- São carregadas uma única vez por processo, na primeira análise, e tratadas como imutáveis durante a execução. Alterar uma lista exige reiniciar o serviço.
- Cada item é canonizado como o host (minúsculas, sem ponto final e sem ``www.`` inicial) antes da comparação exata (RF-15, N-07). Um subdomínio de um item **não** corresponde ao item.
- Um arquivo **ausente** equivale a uma lista vazia, e o carregamento emite um aviso (`WARNING`, logger `analyzer.blocklist`) com o nome do arquivo, para que a falta de uma lista não passe despercebida. A análise continua normalmente.
- Um arquivo com JSON inválido, que não seja um array ou que tenha item que não seja string é erro de configuração (`InvalidDomainListError`): a análise falha em vez de classificar a URL, para que uma lista corrompida nunca produza um resultado `segura` falso.

---

## 5. Contratos de Entrada/Saída (API Contracts)

### 5.1. POST /api/v1/analyze — Request

Content-Type: `application/json`

```json
{
  "url": "http://paypa1-secure.verify-account.top/login"
}

```

| Campo | Tipo | Obrigatório | Restrições |
| --- | --- | --- | --- |
| `url` | string | sim | 1 a 2048 caracteres; URL absoluta; esquema http ou https; host obrigatório |

### 5.2. `POST /api/v1/analyze` — Response 200

```json
{
  "url": "http://paypa1-secure.verify-account.top/login",
  "normalized_host": "paypa1-secure.verify-account.top",
  "score": 70,
  "classification": "perigosa",
  "reasons": [
    "tld_suspeito",
    "possivel_impersonacao_marca:paypal",
    "sem_https",
    "palavra_chave_sensivel_no_path_query"
  ]
}

```

Demonstração do score do exemplo: 15 (TLD .top) + 25 (impersonação paypal) + 10 (HTTP) + 20 (palavra login, liberada pela RN-06) = 70. Não há pontuação por excesso de subdomínios nesse host

| Campo | Tipo | Descrição |
| ---- | --- | --- |
| url | string | Entrada original após trim de espaços externos. |
| normalized_host | string | Host canônico em minúsculas, sem porta, sem ponto final e convertido para IDNA ASCII quando aplicável. |
| score | integer | Valor final entre 0 e 100. |
| classification | string | Um de: segura, suspeita, perigosa. |
| reasons | array[string] | Motivos em ordem normativa determinística. Sem duplicação por heurística. |

> Nota: O campo checked_at foi removido do contrato para preservar RNF-02. Caso observabilidade temporal seja necessária no futuro, ela deverá ser tratada como metadado não determinístico explicitamente excluído dos testes de igualdade do resultado analítico.

### 5.3. Erro de Validação - HTTP 422

Entradas inválidas não retornam HTTP 400 nesta versão. O contrato é padronizado em HTTP 422 para erros de validação de request e de URL.

**Response 422 Unprocessable Entity**:

```json
{
  "detail": "URL inválida: informe uma URL absoluta com esquema http ou https e host válido."
}
```

Para campo ausente, null, vazio, tipo incorreto ou tamanho fora de 1–2048 caracteres, a aplicação deve retornar HTTP 422 com detail descritivo. A implementação pode usar handler de exceção próprio para normalizar o formato do erro do Pydantic/FastAPI, desde que o contrato de status e mensagem permaneça testável.

**Como foi implementado:** existem duas origens de 422, e as duas devolvem `{"detail": "<string>"}`:

| Origem | Quando | Formato de `detail` | Exemplo |
| --- | --- | --- | --- |
| Validação do body (Pydantic) | campo ausente, tipo incorreto, tamanho fora de 1–2048 | `"<local>: <mensagem>"`; vários erros separados por `"; "` | `body -> url: Field required` |
| `InvalidURLError` (normalizador) | URL que não passa nas regras N-01 a N-09 | mensagem iniciada por `URL inválida:` | `URL inválida: esquema 'ftp' não suportado.` |

O texto das mensagens do Pydantic depende da versão da biblioteca. Por isso os testes verificam o status 422 e o formato `{"detail": "<string não vazia>"}`, e não o texto exato.

### 5.4. Regras de normalização da URL

| ID | Regra |
| ------ | ------- |
| N-01 | A entrada deve ser uma string; espaços externos são removidos antes da validação. |
| N-02 | Após trim, o comprimento deve estar entre 1 e 2048 caracteres. |
| N-03 | O esquema é obrigatório e deve ser http ou https, comparado sem distinção de maiúsculas/minúsculas. |
| N-04 | O host é obrigatório. A ausência de host gera InvalidURLError/HTTP 422. Host com espaço em branco ou com label vazio (ex.: `a..b.com`) também é inválido. |
| N-05 | O hostname é convertido para minúsculas, o ponto final absoluto é removido e a porta não faz parte de normalized_host. Uma porta malformada ou fora de 0–65535 invalida a URL. |
| N-06 | Hosts IDN/Unicode são convertidos para IDNA ASCII para normalized_host. O host original deve permanecer disponível ao motor de heurísticas para RF-11. Se a conversão IDNA falhar, a URL é inválida. Hosts já ASCII não passam pela conversão. |
| N-07 | O prefixo `www.` é removido somente para consultas à allowlist/blocklist. O normalized_host da resposta preserva `www.` caso ele faça parte do host de entrada. |
| N-08 | Path e query são preservados para análise, sendo criada uma visão em minúsculas exclusivamente para comparações case-insensitive. O fragmento não participa da pontuação. |
| N-09 | Credenciais/userinfo válidas sintaticamente não invalidam automaticamente a URL; sua presença com @ é sinalizada por RF-06. |

### 5.5. `GET /health` — Response 200

Endpoint de disponibilidade (RF-16). Não recebe parâmetros, não aciona o motor de análise e não acessa dependências externas.

```json
{
  "status": "ok",
  "service": "phishguard",
  "version": "3.0.0"
}
```

| Campo | Tipo | Descrição |
| ---- | --- | --- |
| status | string | Sempre `ok` quando o serviço responde. |
| service | string | Nome do serviço: `phishguard`. |
| version | string | Versão da release publicada no GitHub, sem o prefixo `v` (tag `v3.0.0` → `3.0.0`). |

A versão é definida em um único ponto, `APP_VERSION` em `analyzer/config.py`, e é a mesma exibida nos metadados OpenAPI (`/docs`). Toda nova release deve atualizar esse valor.

---

## 6. Decomposição em Componentes / Unidades

O sistema é decomposto em unidades isoladas e independentemente testáveis, permitindo
desenvolvimento e testes iterativos por componente (cada uma vira uma *issue* própria no
GitHub Projects). Os módulos ficam no pacote `analyzer/`; as heurísticas ficam em
`analyzer/rules/`, um arquivo por regra:

```text
HTTP Request (JSON)
        │
        ▼
┌──────────────────────┐  valida o body   ┌──────────────────────┐
│ api.py               │─────────────────▶│ models.py            │
│ rotas, handlers 422, │◀─────────────────│ AnalyzeRequest,      │
│ /health              │  serializa       │ AnalyzeResponse,     │
└──────────┬───────────┘                  │ HealthResponse       │
           │ calculate_risk(url)          └──────────────────────┘
           ▼
┌──────────────────────┐  1. normalize()  ┌──────────────────────┐
│ scorer.py            │─────────────────▶│ url_normalizer.py    │
│ precedência e        │                  │ ParsedURL ou         │
│ agregação            │                  │ InvalidURLError      │
│ (RN-01 a RN-09)      │                  └──────────────────────┘
│                      │  2. listas       ┌──────────────────────┐
│                      │─────────────────▶│ blocklist.py         │
│                      │                  │ data/allowlist.json, │
│                      │                  │ data/blocklist.json  │
│                      │                  └──────────────────────┘
│                      │  3. check()      ┌──────────────────────┐
│                      │─────────────────▶│ rules/*.py           │
│                      │                  │ uma heurística por   │
│                      │                  │ arquivo, devolve     │
│                      │                  │ HeuristicResult      │
└──────────┬───────────┘                  └──────────────────────┘
           │ AnalysisResult
           ▼
HTTP Response (JSON)

config.py: pesos, limiares, listas fechadas, limites e APP_VERSION,
lidos por scorer.py, url_normalizer.py, rules/*.py e api.py.
```

Uma URL inválida interrompe o fluxo no passo 1: a `InvalidURLError` sobe até o `api.py`, que responde HTTP 422 (RN-09). Se o host estiver na allowlist ou na blocklist, o passo 3 não é executado (RN-03, RN-04).

| Componente | Responsabilidade única | Testável isoladamente? |
| --- | --- | --- |
| `api.py` | Rotas FastAPI (`POST /api/v1/analyze`, `GET /health`), handlers que convertem erros de validação e `InvalidURLError` em HTTP 422, serialização JSON. Sem regra de phishing. | Sim, via `TestClient` com o scorer substituído por *mock*. |
| `models.py` | Schemas Pydantic dos contratos HTTP: `AnalyzeRequest`, `AnalyzeResponse` e `HealthResponse`. | Via testes de contrato da API. |
| `url_normalizer.py` | Único ponto de parsing de URL: aplica N-01 a N-09 e produz `ParsedURL` ou `InvalidURLError`. Também expõe `is_ip_host`, usado pela RF-05. | Sim, sem dependências externas. |
| `rules/base.py` | Tipo `HeuristicResult` e os construtores `fired(reason)` e `not_triggered()`. | Coberto pelos testes das heurísticas. |
| `rules/*.py` | Uma heurística por arquivo, função pura `check(ParsedURL) -> HeuristicResult`, RF-05 a RF-14. | Sim, isoladamente. |
| `blocklist.py` | Carregar `data/allowlist.json` e `data/blocklist.json` (seção 4.3) e checar o host canônico. | Sim, com listas injetadas ou diretório temporário. |
| `scorer.py` | Orquestrar normalização, listas e heurísticas; aplicar RN-01 a RN-09; produzir `AnalysisResult` (dataclass com os mesmos 5 campos do §5.2). Define a ordem das heurísticas em `STRUCTURAL_HEURISTICS`. | Sim, com `DomainLists` injetado. |
| `config.py` | Fonte em código das constantes desta especificação: `POINTS`, `THRESHOLDS`, `SCORE_MIN`/`SCORE_MAX`, listas fechadas, `MAX_URL_LENGTH`, `MAX_SUBDOMAIN_LEVELS`, `MAX_INPUT_LENGTH` e `APP_VERSION`. | Sim, `test_config_consistency.py` compara as listas com este documento. |

A decomposição permite trabalho paralelo por heurística em branches independentes, desde que todas respeitem a mesma interface e retornem um `HeuristicResult` padronizado.

### 6.1. Interface comum das heurísticas

```python
@dataclass(frozen=True)
class HeuristicResult:
    triggered: bool
    reason: Optional[str] = None   # código da Tabela 4.1 quando triggered=True

def check(parsed: ParsedURL) -> HeuristicResult: ...
```

- A heurística **não** devolve pontos. O `scorer.py` obtém a pontuação em `config.POINTS[reason]`, o que mantém os pesos num lugar só.
- Motivos parametrizados, como `possivel_impersonacao_marca:<marca>`, usam a parte anterior ao `:` como chave de pontuação. Um motivo sem entrada em `POINTS` gera erro em vez de valer zero.
- A ordem de execução é a tupla `STRUCTURAL_HEURISTICS` do `scorer.py`, na ordem normativa do §4.1. A palavra-chave sensível fica fora da tupla e é avaliada por último, porque depende da RN-06.

### 6.2. Decisões arquiteturais

As decisões que justificam esta arquitetura estão em `docs/adr/` (índice em `docs/adr/README.md`): ADR-0001 (Python 3.11 + FastAPI), ADR-0002 (heurísticas em vez de ML), ADR-0003 (serviço stateless, sem banco), ADR-0004 (Docker e Docker Compose), ADR-0005 (Claude Code como agente de IA), ADR-0006 (subdomínios sem Public Suffix List), ADR-0007 (marca por inclusão e leet speak), ADR-0008 (contrato determinístico, sem `checked_at`) e ADR-0009 (CI com GitHub Actions). Todas estão com status "Aceita" na versão 3.0.0.

---

## 7. Casos de Teste / Test Harness

Todos os cenários e casos de borda abaixo têm teste automatizado na suíte entregue.

**Cenários principais:** URL claramente segura (domínio em `allowlist` ou sem sinais de risco);
URL claramente perigosa (múltiplas heurísticas + domínio em `blocklist`); URL intermediária
(1–2 sinais fracos) classificada como `suspeita`.

**Casos de borda (edge cases):**

- URL vazia, `None` ou tipo incorreto;
- URL sem esquema (``www.`exemplo.com`);
- Host como IPv4 (`http://192.168.0.1/login`) e IPv6;
- URL com `@` (`http://usuario@dominio-falso.com@dominio-real.com`);
- Domínio Punycode (`http://xn--pple-43d.com`);
- Domínio com homoglifo unicode (`http://аpple.com` — "а" cirílico);
- URL de encurtador conhecido;
- URL com mais de 2048 caracteres;
- Domínio com muitos subdomínios (`a.b.c.d.e.exemplo.com`);
- Domínio oficial de marca monitorada (não deve disparar impersonação — RN-05);
- URL com palavra sensível mas sem nenhum outro sinal (não deve subir de faixa — RN-06);
- Mesma URL testada duas vezes deve retornar exatamente o mesmo resultado (RNF-02).

---

### 7.1. Organização da suíte

Cada heurística tem o seu arquivo em `tests/unit/`, com casos positivo, negativo e de borda. Os testes de `tests/integration/` exercitam a API (`test_api.py`, com o scorer substituído por *mock*), o fluxo completo do scorer com as listas reais (`test_detector.py`) e o RNF-01 (`test_performance.py`).

```text
tests/
├── unit/
│   ├── test_at_symbol.py
│   ├── test_blocklist.py
│   ├── test_brand_impersonation.py
│   ├── test_config_consistency.py
│   ├── test_excessive_subdomains.py
│   ├── test_ip_domain.py
│   ├── test_missing_https.py
│   ├── test_punycode_homograph.py
│   ├── test_scorer.py
│   ├── test_suspicious_keywords.py
│   ├── test_suspicious_tld.py
│   ├── test_url_length.py
│   ├── test_url_normalizer.py
│   └── test_url_shortener.py
├── integration/
│   ├── test_api.py
│   ├── test_detector.py
│   └── test_performance.py
```

> Os testes de desempenho devem usar tolerância adequada ao ambiente e não substituir os testes funcionais. O RNF-01 é validado pela média de várias análises (limite de 300 ms por URL), evitando flutuações excessivas em um único teste de CI.

### 7.2. Execução, cobertura e evidências

O `pytest.ini` define `testpaths = tests` e ativa a cobertura em toda execução (`--cov=analyzer --cov-branch --cov-report=term-missing`, via `pytest-cov`). Não há percentual mínimo obrigatório.

| Forma de execução | Comando | Evidência gerada |
| --- | --- | --- |
| Local | `./scripts/run_harness.sh` | Log em `logs/harness_<data>_<hora>.log` (não versionado) |
| Ambiente padronizado | `docker compose run --rm test` (o serviço `test` executa o `scripts/run_harness.sh`) | Log em `logs/harness_<data>_<hora>.log` no diretório do projeto, pelo volume montado (não versionado) |
| CI, job `Test Harness (pytest)` | `python -m pytest` no GitHub Actions | Artefato `evidencias-test-harness`: `logs_test_harness.txt`, `test-report.xml` (JUnit), `coverage.xml` e `htmlcov/`, guardado por 30 dias |
| CI, job `Test Harness (Docker)` | `docker compose run --rm test` | Log do job no GitHub Actions (o arquivo em `logs/` fica no runner e não é publicado) |

Os dois jobs de CI rodam em todo push e PR para `main` e `develop`, e são checks obrigatórios do ruleset dessas branches, que também exige um PR com uma aprovação (ADR-0009). Os números de testes e de cobertura da release estão no relatório de testes da Etapa Final, em `docs/evidencias/`.

---

## 8. Refinamento por Feedback

**Data**: 2026-10-22
**Descrição**: Decisões sobre os três pontos deixados em aberto pela revisão As-Built: (1) o serviço `test` do `docker-compose.yml` passa a executar o `scripts/run_harness.sh`, de modo que `docker compose run --rm test` também grava o log em `logs/` e cumpre o RNF-06 (§7.2); (2) arquivo de lista local ausente continua equivalendo a lista vazia, mas passa a emitir um aviso no log (§4.3); (3) a busca de palavra-chave por substring e a exigência de outro sinal da RN-06 são mantidas sem alteração (§4.2). Nenhum peso, limiar, lista ou contrato HTTP foi alterado.
**Justificativa** (Issue #133): O RNF-06 exige log persistido em toda execução da suíte, o que o comando Docker não cumpria. Uma lista ausente sem aviso podia desativar o bloqueio silenciosamente. Quanto ao ponto 3, foi sugerido pontuar a palavra-chave sozinha; o grupo optou por manter a RN-06, porque a substring gera falsos positivos (`/blogin`, `/updates`) que só são contidos pela exigência de outro sinal. Respostas de @anaacllara na issue e decisão final de @mariisena em 2026-10-22.

**Data**: 2026-10-20
**Descrição**: Revisão As-Built para a release `v3.0.0`, sem alteração de regra de negócio, peso, limiar, lista ou contrato. O documento foi conferido seção por seção contra o código entregue e passou a registrar comportamentos que já existiam no código e nos testes mas não estavam descritos: critérios de TLD, URL longa, palavra-chave por substring e marca com mais de uma ocorrência (§4.2); carregamento e erros das listas locais (novo §4.3); as duas origens e formatos do HTTP 422 (§5.3); host com espaço ou label vazio, porta inválida e falha de IDNA (N-04 a N-06). Também foram corrigidos: o diagrama e a tabela de componentes do §6, que não refletiam as dependências reais (incluídos `rules/base.py`, `AnalysisResult` e `APP_VERSION`); o §6.1, que previa um campo `points` no `HeuristicResult` que nunca existiu (a pontuação é do `scorer.py`); a organização da suíte e a execução e evidências do harness (§7.1 e novo §7.2); e as referências às ADRs (novo §6.2).
**Justificativa** (Issue #133): A Etapa Final exige uma especificação As-Built que reflita rigorosamente o que foi entregue. Como o SDD é a fonte da verdade, as divergências apenas documentais foram corrigidas aqui; nenhuma delas exigiu mudar código.

**Data**: 2026-10-20
**Descrição**: O RF-16 passa a remeter ao novo §5.5, que documenta o contrato do `GET /health` (campos `status`, `service` e `version`). O campo `version` passa a informar a versão da release (`3.0.0`), definida em `APP_VERSION` no `analyzer/config.py`, em vez do valor fixo `1.0.0` que estava escrito em dois pontos do `api.py`.
**Justificativa** (Issue #132): A preparação da Etapa Final mostrou que o contrato do `/health` existia apenas no código e que a versão informada (`1.0.0`) não correspondia às releases publicadas (`v2.0.0` a `v2.0.2`). A decisão de alinhar a versão à release final `v3.0.0` foi tomada por @mariisena em 2026-10-20.

**Data**: 2026-10-13
**Descrição**: Documentação da limitação conhecida da RN-05: a busca do nome da marca por substring pode sinalizar palavras legítimas, como `capitaurbana.com` (itau) e `caixadesom.com` (caixa). Testes adicionados para preservar esse comportamento especificado, sem alteração da heurística.
**Justificativa** (PR #88): A limitação foi levantada durante a revisão do PR #88. Como a detecção por inclusão está dentro do escopo definido e typosquatting avançado está fora de escopo, a mudança registra os falsos positivos conhecidos e evita alteração acidental da regra.

**Data**: 2026-10-13
**Descrição**: Reorganização dos testes em `tests/unit/` e `tests/integration/`, mantendo as evidências geradas pelo harness em `logs/`.
**Justificativa**: Alinhar a estrutura do repositório ao §7.1 do SDD após a divergência deixada pela issue #66, encerrada como concluída sem a reorganização correspondente.

**Data**: 2026-10-13
**Descrição**: O RF-09 passou a adotar correspondência por sufixo com fronteira de ponto, além da igualdade exata já existente. O host dispara se for igual ao encurtador ou se terminar em `"." + encurtador`. Exemplos: ``www.`bit.ly` e `m.bit.ly` passam a disparar; `notbit.ly` (sem fronteira) e `bit.ly.evil.com` (encurtador no meio) continuam não disparando.
**Justificativa** (Issue #90 / PR #88): A correspondência puramente exata permitia que``www.`bit.ly` escapasse da heurística, pois o N-07 remove o ``www.`` apenas nas consultas à allowlist/blocklist, e não nas heurísticas. O grupo decidiu pela opção B: cobrir subdomínios de encurtadores conhecidos, evitando que o usuário comum que copia ou digita links com ``www.`` contorne a detecção.

**Data**: 2026-10-11
**Descrição**: Revisão de consistência pós-Entrega 1, sem alteração de regra de negócio, peso, limiar ou lista: (a) RF-01 passa a citar o endpoint correto `POST /api/v1/analyze`; (b) o campo `checked_at` foi retirado do exemplo de response do §5.2, alinhando o exemplo à nota do próprio §5.2 que já o removera do contrato por causa do RNF-02; (c) as URLs dos exemplos JSON dos §5.1/§5.2 deixam de conter sintaxe de link Markdown dentro da string; (d) o §6 passa a refletir a localização real das heurísticas (`analyzer/rules/`); (e) o §7 corrige referências de regra (impersonação → RN-05, palavra-chave → RN-06); (f) remoção de itens duplicados no §1.1.
**Justificativa**: A revisão do repositório no início da Entrega 2 identificou divergências entre o texto do SDD, o código e os testes. Como o SDD é a fonte da verdade, as divergências puramente documentais foram corrigidas aqui; a remoção de `checked_at` do código (`models.py`/`api.py`) é tratada em alteração separada, seguindo esta especificação.

**Data**: 2026-09-15
**Descrição**: O exemplo de response JSON na seção 5.2 usava o código de motivo `"palavra_chave_sensivel_no_path"`, inconsistente com o código normativo `"palavra_chave_sensivel_no_path_query"` definido na Tabela 4.1.
**Justificativa** (Issue #60): A Tabela 4.1 é a referência normativa do sistema e o código já usa essa convenção. Tratava-se de uma inconsistência apenas na documentação; nenhum arquivo de código ou teste foi alterado.

**Data**: 2026-09-12
**Descrição**: A regra RN-05 foi atualizada para formalizar a aplicação de normalização leet speak básica (0→o, 1→l, 3→e, 4→a, 5→s, 7→t) antes da verificação de impersonação de marcas.
**Justificativa**: A decisão do grupo (#59) confirmou que o teste normativo `test_exemplo_normativo_do_sdd` em `tests/test_scorer.py` já depende desse comportamento para atingir o score esperado no host `paypa1-secure.verify-account.top`. Alterar o código invalidaria a suíte de testes existente, então a documentação foi adaptada para espelhar a implementação.

**Data**: 2026-09-12
**Descrição**: As listas fechadas da seção 4.2 (SUSPICIOUS_TLDS, URL_SHORTENERS, MONITORED_BRANDS) foram ampliadas para espelhar as configurações já existentes e validadas em `analyzer/config.py`.
**Justificativa**: A decisão do grupo (#58) definiu que reduzir o código descartaria configurações já validadas e poderia quebrar implementações futuras. Optou-se por ampliar o SDD para ser compatível com o código e inserir um teste de consistência automatizado para garantir que ambos permaneçam em sincronia (onde o SDD é ajustado ao config de forma documentada neste refinamento).

---

## 9. Histórico de Versões

| Versão | Data | Alteração | Motivo | Autor |
| --- | --- | --- | --- | --- |
| v1.0 | 2026-09-03 | Criação do documento | Especificação inicial para o Bootcamp | Ana Clara |
| v1.1 | 2026-09-08 | Correção de numerações (RN), remoção de conflito de SLA (RNF) e ajustes nos contratos de erro da API (422). | Refinamento após revisão de arquitetura | Mariana |
| v1.2 | 2026-09-12 | Ampliação das listas fechadas da seção 4.2 para parear com o config.py. | Refinamento por Feedback (#58) | Ana Clara |
| v1.2 | 2026-09-12 | Atualização da RN-05 para admitir normalização leet speak básica. | Refinamento por Feedback (#59) | Ana Clara |
| v1.2 | 2026-09-17 | Correção da flag para palavra_chave_sensivel_no_path_query no §5.2. | Refinamento por Feedback (#60) | Ana Clara |
| v1.2 | 2026-09-22 | Definição de escopo e conteúdo inicial das listas de allowlist e blocklist. | Refinamento por Feedback (#61) | Ana Clara |
| v1.3 | 2026-10-11 | Revisão de consistência: endpoint do RF-01, remoção de `checked_at` do exemplo §5.2, localização das heurísticas, referências RN no §7. | Revisão pós-Entrega 1 | Mariana |
| v1.3 | 2026-10-13 | Documentação da limitação da RN-05 para marcas contidas em palavras legítimas; testes fixam `capitaurbana.com` e `caixadesom.com`. | Refinamento por Feedback (PR #88) | Ana Clara |
| v1.3 | 2026-10-13 | Estende a verificação de subdomínios de encurtadores para RF-09 | Atualização após discussão em grupo | Ana Clara |
| v1.4 | 2026-10-20 | Contrato do `GET /health` no §5.5; `version` passa a ser a versão da release (`3.0.0`), centralizada em `APP_VERSION`. | Refinamento por Feedback (#132) | Mariana |
| v3.0 | 2026-10-20 | **Versão As-Built** da release `v3.0.0`: SDD conferido contra o código; comportamentos implementados e não descritos passam a constar (§4.2, §4.3, §5.3, §5.4); §6 (diagrama, componentes, interface, ADRs) e §7 (suíte, cobertura, evidências) refletem o entregue. A numeração do documento passa a acompanhar a release. | Etapa Final (#133) | Mariana |
| v3.0 | 2026-10-22 | Decisões da revisão As-Built: `docker compose run --rm test` grava log em `logs/` (§7.2); lista local ausente emite aviso (§4.3); RF-14 por substring e RN-06 mantidos (§4.2). | Refinamento por Feedback (#133) | Mariana |
