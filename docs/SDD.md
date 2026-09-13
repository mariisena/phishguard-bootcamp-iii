# Especificação Técnica — Spec-Driven Development (SDD)

**Projeto:** PhishGuard — Detector de URLs Suspeitas/Phishing
**Disciplina:** Bootcamp III — Turma B-0726
**Entrega:** 1 — Ambiente, Especificação Técnica e Test Harness
**Metodologia:** Spec-Driven Development (SDD)
**Versão do documento:** 1.0
**Última atualização:** ver seção 8 (Histórico de Versões)

---

## 1. Descrição do Problema

Phishing é uma das formas mais comuns de fraude digital: um atacante cria ou distribui uma URL que imita um site legítimo (bancos, e-mail, redes sociais, serviços de pagamento) para induzir a vítima a fornecer credenciais, dados pessoais ou financeiros. Grande parte dessas URLs apresenta padrões estruturais reconhecíveis — mesmo sem consultar bases externas em tempo real — como uso de IP no lugar de domínio, presença do caractere `@`, domínios com aparência de marcas conhecidas, uso de encurtadores, excesso de subdomínios ou caracteres unicode que imitam letras latinas (homograph/punycode).

O **PhishGuard** é um serviço (API HTTP) que recebe uma URL e retorna uma avaliação de risco (pontuação de 0 a 100 e uma classificação categórica), explicando quais sinais de risco foram identificados. O objetivo da Entrega 1 é especificar o problema, decompor a solução em unidades testáveis e entregar um *harness* de testes automatizado que valide as regras de negócio definidas abaixo — a implementação de referência incluída no repositório serve como prova de conceito para validar a especificação e os testes.

### 1.1 Fora de escopo (nesta entrega)

- Consulta a serviços externos de reputação de URL (Google Safe Browsing, VirusTotal etc.) — candidato a evolução futura (ver ADR-0002).
- Persistência em banco de dados — o serviço é *stateless* nesta versão (ver ADR-0003).
- Autenticação/autorização de usuários da API.
- Interface gráfica (o consumo é via API HTTP; a suíte de testes cobre o contrato da API).
- Resolução ou acompanhamento de redirecionamentos de URLs encurtadas.
-Persistência em banco de dados; o serviço não mantém estado persistente entre requisições.
-	Autenticação e autorização de consumidores da API.
-	Interface gráfica; o consumo é exclusivamente via API HTTP.
-	Detecção avançada de typosquatting por distância de edição, modelos de linguagem ou aprendizado de máquina. Nesta versão, a regra de marca cobre impersonação por inclusão do nome da marca no host.
-	Uso de Public Suffix List externa; a regra de subdomínios utiliza uma aproximação determinística definida na seção 4.2.

---

## 2. Requisitos Funcionais (RF)

| ID | Requisito |
|----|-----------|
| **RF-01** | O sistema deve receber uma URL (string) via `POST /analyze` e retornar uma pontuação de risco de 0 a 100. |
| **RF-02** | O sistema deve classificar a URL em `segura` (0–29), `suspeita` (30–59) ou `perigosa` (60–100). |
| **RF-03** | O sistema deve retornar uma lista ordenada de motivos que justifique a pontuação ou eventual sobreposição por lista local. |
| **RF-04** | O sistema deve normalizar e validar a entrada antes da análise, aceitando apenas URLs HTTP(S) absolutas com host válido. |
| **RF-05** | O sistema deve identificar quando o host é um endereço IP IPv4 ou IPv6 em vez de um nome de domínio. |
| **RF-06** | O sistema deve identificar uso do caractere @ na seção de autoridade/userinfo da URL, sinal associado à ocultação do host real. |
| **RF-07** | O sistema deve identificar excesso de subdomínios conforme a regra operacional definida na seção 4.2. |
| **RF-08** | O sistema deve identificar TLDs da lista fechada de TLDs suspeitos definida nesta especificação. |
| **RF-09** | O sistema deve identificar domínios pertencentes à lista fechada de encurtadores conhecidos. |
| **RF-10** | O sistema deve identificar possível impersonação de marcas monitoradas quando o host contiver o nome da marca, mas não pertencer ao domínio oficial cadastrado para essa marca. |
| **RF-11** | O sistema deve identificar hosts em Punycode (xn--) ou hosts originalmente informados com caracteres não ASCII/Unicode. |
| **RF-12** | O sistema deve identificar ausência de HTTPS quando o esquema da URL for http. |
| **RF-13** | O sistema deve identificar URLs anormalmente longas (mais de 75 caracteres). |
| **RF-14** | O sistema deve identificar palavras-chave sensíveis no path ou query, de forma case-insensitive, e pontuá-las apenas quando ao menos outra heurística RF-05 a RF-13 tiver disparado. |
| **RF-15** | O sistema deve checar allowlist e blocklist locais por correspondência exata do host canônico; allowlist e blocklist sobrepõem o resultado heurístico conforme as regras de negócio. |
| **RF-16** | O sistema deve expor GET /health e retornar um JSON de disponibilidade. |
| **RF-17** | Entradas ausentes, nulas, vazias, de tipo incorreto, fora do limite de tamanho ou URLs inválidas devem retornar HTTP 422 com mensagem descritiva, sem exceção não tratada. |

---

## 3. Requisitos Não-Funcionais (RNF)

| ID | Requisito | Descrição |
|----|-----------|
| **RNF-01** | **Desempenho** | Cada análise deve ser concluída em até 300 ms em ambiente de desenvolvimento padrão, sem chamadas de rede a terceiros e com processamento predominantemente em memória. |
| **RNF-02** | **Determinismo** | Para a mesma entrada e a mesma versão de configuração/listas, url, normalized_host, score, classification e reasons devem ser idênticos. A ordem de reasons também é determinística. |
| **RNF-03** | **Testabilidade** | Cada heurística deve ser uma função pura testável isoladamente da camada HTTP e das demais heurísticas. |
| **RNF-04** | **Extensibilidade** | Novas heurísticas devem poder ser adicionadas por meio da mesma interface de entrada/saída, sem alterar o contrato das heurísticas existentes. |
| **RNF-05** | **Portabilidade** | O serviço deve executar de forma reproduzível por docker compose up, sem configuração manual específica do ambiente do desenvolvedor além de Docker/Compose. |
| **RNF-06** | **Observabilidade mínima** | Toda execução da suíte deve gerar relatório ou log persistido em arquivo como evidência de execução. |
| **RNF-07** | **Internacionalização de entrada** | O normalizador deve aceitar URLs contendo IDN/Unicode sem lançar exceção não tratada e deve produzir representação canônica determinística. |
| **RNF-08** | **Stack tecnológica** | A aplicação deve ser desenvolvida em Python com FastAPI e schemas Pydantic, visando simplicidade, conteinerização e reprodutibilidade. |
| **RNF-09** | **Contrato JSON** | Os corpos de request e response da API devem utilizar JSON. Respostas de erro previstas também devem ser serializadas em JSON. | 
| **RNF-10** | **Modularidade** | O código deve separar claramente camada HTTP, modelos de contrato, normalização, heurísticas, listas locais e agregação/scoring. | 


---

## 4. Regras de Negócio (RN)

1. **RN-01 — Pontuação cumulativa e limitada:** Cada heurística disparada soma seus pontos uma única vez. O score heurístico final é limitado ao intervalo [0, 100] por clamp.
2. **RN-02 — Classificação por faixa:** Score de 0 a 29 resulta em segura; 30 a 59 em suspeita; 60 a 100 em perigosa. As faixas são constantes centralizadas e não devem ser repetidas de forma hardcoded.
3.	**RN-03 — Allowlist tem prioridade absoluta:** Se o host canônico, sem prefixo www., corresponder exatamente a um item da allowlist, o resultado final deve ser score 0, classification segura e reasons = ["dominio_allowlist"]. A allowlist é avaliada antes da blocklist.
4.	**RN-04 — Blocklist força classificação perigosa:** Se o host canônico, sem prefixo www., corresponder exatamente a um item da blocklist e não houver correspondência na allowlist, o resultado final deve ser score 100, classification perigosa e reasons = ["dominio_blocklist"].
5.	**RN-05 — Impersonação de marca exige ausência de domínio oficial:** A heurística dispara quando o host contém, de forma case-insensitive, o nome de uma marca monitorada e o host não é o domínio oficial nem um subdomínio desse domínio oficial. A heurística representa impersonação por inclusão de marca; typosquatting por variação ortográfica permanece fora de escopo.
6.	**RN-06 — Palavra-chave sensível exige outro sinal:** A presença de palavra-chave sensível no path/query só adiciona pontos se ao menos uma heurística RF-05 a RF-13 também tiver disparado. Múltiplas palavras ou ocorrências não acumulam pontos adicionais.
7.	**RN-07 — Uma heurística dispara no máximo uma vez:** Cada categoria de heurística soma pontos no máximo uma vez por análise, ainda que o padrão apareça repetidamente.
8.	**RN-08 — Encurtadores são sinalizados, não bloqueados:** Host de encurtador conhecido adiciona pontuação e o motivo encurtador_conhecido_destino_nao_verificado. O serviço não segue o redirecionamento nesta entrega.
9.	**RN-09 — Entrada inválida não recebe classificação:** Se a entrada não puder ser validada/normalizada, a API retorna HTTP 422 e não produz score, classification ou reasons de análise.

> Nota: A allowlist e a blocklist não devem conter o mesmo host. O Test Harness deve incluir um teste de consistência de configuração para detectar interseção entre as duas listas. Caso exista interseção por erro de configuração, RN-03 ainda prevalece por definição.

## 4.1. Pontuação normativa e códigos de motivo

| Heurística	| Pontos | reason |
|-------------|:------:|--------|
| Host é IPv4/IPv6 | 25 | host_ip |
| Uso de @ na autoridade/userinfo | 25 | uso_arroba_userinfo |
| Excesso de subdomínios | 15	| subdominios_excessivos |
| TLD suspeito | 15 | tld_suspeito |
| Encurtador conhecido | 15 | encurtador_conhecido_destino_nao_verificado |
| Possível impersonação de marca	| 25 | possivel_impersonacao_marca:<marca> |
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

**Critério de subdomínios nesta entrega**: para hosts que não são IP, o hostname é separado por pontos. Para manter a implementação local e determinística sem Public Suffix List, os dois últimos labels são tratados como domínio-base; a heurística dispara quando houver mais de três labels anteriores a esses dois. Portanto, a.b.c.d.example.com dispara (4 subdomínios) e a.b.c.example.com não dispara (3). Essa aproximação é conhecida e poderá ser substituída por uma Public Suffix List em evolução futura.

**Critério de Punycode/Unicode**: a heurística dispara se o host original possuir qualquer caractere não ASCII ou se a forma canônica IDNA contiver label iniciado por xn--. O normalizador deve preservar informação suficiente para essa checagem antes/depois da conversão IDNA.

**Critério do caractere @**: a regra considera @ na seção de autoridade/userinfo, isto é, entre // e o início de path/query/fragmento. Um @ apenas no path/query não deve disparar RF-06.

---

## 5. Contratos de Entrada/Saída (API Contracts)

### 5.1. POST /api/v1/analyze — Request

Content-Type: `application/json`

```json
{
  "url": "[http://paypa1-secure.verify-account.top/login](http://paypa1-secure.verify-account.top/login)"
}

```

| Campo | Tipo | Obrigatório | Restrições |
| --- | --- | --- | --- |
| `url` | string | sim | 1 a 2048 caracteres; URL absoluta; esquema http ou https; host obrigatório |

### 5.2. `POST /api/v1/analyze` — Response 200

```json
{
  "url": "[http://paypa1-secure.verify-account.top/login](http://paypa1-secure.verify-account.top/login)",
  "normalized_host": "paypa1-secure.verify-account.top",
  "score": 70,
  "classification": "perigosa",
  "reasons": [
    "tld_suspeito",
    "possivel_impersonacao_marca:paypal",
    "sem_https",
    "palavra_chave_sensivel_no_path"
  ],
  "checked_at": "2026-08-31T13:00:00Z"
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

### 5.4. Regras de normalização da URL

| ID | Regra |
| ------ | ------- |
| N-01 | A entrada deve ser uma string; espaços externos são removidos antes da validação. |
| N-02 | Após trim, o comprimento deve estar entre 1 e 2048 caracteres. |
| N-03 | O esquema é obrigatório e deve ser http ou https, comparado sem distinção de maiúsculas/minúsculas. |
| N-04 | O host é obrigatório. A ausência de host gera InvalidURLError/HTTP 422. |
| N-05 | O hostname é convertido para minúsculas, o ponto final absoluto é removido e a porta não faz parte de normalized_host. |
| N-06 | Hosts IDN/Unicode são convertidos para IDNA ASCII para normalized_host. O host original deve permanecer disponível ao motor de heurísticas para RF-11. |
| N-07 | O prefixo www. é removido somente para consultas à allowlist/blocklist. O normalized_host da resposta preserva www. caso ele faça parte do host de entrada. |
| N-08 | Path e query são preservados para análise, sendo criada uma visão em minúsculas exclusivamente para comparações case-insensitive. O fragmento não participa da pontuação. |
| N-09 | Credenciais/userinfo válidas sintaticamente não invalidam automaticamente a URL; sua presença com @ é sinalizada por RF-06. |

---

## 6. Decomposição em Componentes / Unidades

O sistema é decomposto em unidades isoladas e independentemente testáveis, permitindo
desenvolvimento e testes iterativos por componente (cada uma vira uma *issue* própria no
GitHub Projects — ver `GITHUB_SETUP.md`):

```text
┌──────────────┐ 
│ HTTp Request │
└──────┬───────┘
       │
       ▼
  ┌──────────────┐     ┌──────────────────┐      ┌───────────────┐
  │  api.py      │────▶│  scorer.py       │────▶│  models.py    │
  │ (FastAPI,    │     │ (agrega heurísti-│      │ (contratos/   │
  │  contrato    │     │  cas + blocklist │      │  schemas      │
  │  HTTP)       │     │  + allowlist →   │      │  Pydantic)    │
  └──────────────┘     │  score+classific.)      └───────────────┘
                       └────────┬─────────┘
                                ▼
┌──────────────┐     ┌────────────────────┐
│url_normalizer│     │  heuristics/*.py   │
│.py (parse +  │◀───│  (uma função pura   │
│ validação)   │     │  por regra de      │
└──────────────┘     │  negócio RF-05..14)|
                     └────────┬───────────┘
                              ▼
                     ┌──────────────────┐
                     │  blocklist.py    │
                     │ (allowlist/      │
                     │  blocklist locais)
                     └──────────────────┘

```

| Componente | Responsabilidade única | Testável isoladamente? |
| --- | --- | --- |
| `models.py` | Schemas Pydantic de request/response e tipos compartilhados. | Via testes de contrato e validação de schema. |
| `url_normalizer.py` | Validar e parsear a URL; produzir `ParsedURL` e InvalidURLError em entradas inválidas. | Sim — sem dependências externas. |
| `heuristics/*.py` | Uma regra por módulo/função pura: (`ParsedURL`) -> `HeuristicResult`. | Sim, isoladamente. |
| `scorer.py` | Orquestrar normalização, listas e heurísticas; aplicar RN-01 a RN-09; produzir `AnalysisResult`. | Sim, via *fakes*/*fixtures*. |
| `blocklist.py` | Carregar `allowlist.json` e `blocklist.json` locais e checar host canônico. | Sim, com fixtures/listas de teste. |
| `api.py` |Rotas FastAPI, tratamento de erros e serialização JSON. | Sim, via `TestClient`. |
| `config.py` | Fonte normativa em código para POINTS, THRESHOLDS, listas fechadas e ordem das heurísticas, refletindo esta especificação. | Sim, por testes de consistência/configuração. |

A decomposição permite trabalho paralelo por heurística em branches independentes, desde que todas respeitem a mesma interface e retornem um `HeuristicResult` padronizado.


### 6.1. Interface comum sugerida para heurísticas

```
HeuristicResult:
  triggered: bool
  points: int
  reason: str | None

heuristic(parsed_url: ParsedURL) -> HeuristicResult
```

O scorer não deve depender de detalhes internos de cada heurística. A ordem de execução deve ser definida em uma coleção única e estável, permitindo extensibilidade e determinismo.

---

## 7. Casos de Teste Previstos / Test Harness

**Cenários principais:** URL claramente segura (domínio em `allowlist` ou sem sinais de risco);
URL claramente perigosa (múltiplas heurísticas + domínio em `blocklist`); URL intermediária
(1–2 sinais fracos) classificada como `suspeita`.

**Casos de borda (edge cases):**

* URL vazia, `None` ou tipo incorreto;
* URL sem esquema (`www.exemplo.com`);
* Host como IPv4 (`http://192.168.0.1/login`) e IPv6;
* URL com `@` (`http://usuario@dominio-falso.com@dominio-real.com`);
* Domínio Punycode (`http://xn--pple-43d.com`);
* Domínio com homoglifo unicode (`http://аpple.com` — "а" cirílico);
* URL de encurtador conhecido;
* URL com mais de 2048 caracteres;
* Domínio com muitos subdomínios (`a.b.c.d.e.exemplo.com`);
* Domínio oficial de marca monitorada (não deve disparar impersonação — RN-06);
* URL com palavra sensível mas sem nenhum outro sinal (não deve subir de faixa — RN-07);
* Mesma URL testada duas vezes deve retornar exatamente o mesmo resultado (RNF-02).


7.1. Organização sugerida da suíte

```bash

tests/
├── unit/
│   ├── test_url_normalizer.py
│   ├── test_heuristics_*.py
│   ├── test_scorer.py
│   └── test_config_consistency.py
├── integration/
│   ├── test_analyze_api.py
│   └── test_health_api.py
└── evidence/
    └── test-report.xml / test-report.txt

```

> Os testes de desempenho devem usar tolerância adequada ao ambiente e não substituir os testes funcionais. O requisito RNF-01 pode ser validado por benchmark dedicado ou medição agregada, evitando flutuações excessivas em um único teste de CI.
> 
---

## 8. Refinamento por Feedback

**Data**: 2026-09-12
**Descrição**: As listas fechadas da seção 4.2 (SUSPICIOUS_TLDS, URL_SHORTENERS, MONITORED_BRANDS) foram ampliadas para espelhar as configurações já existentes e validadas em `analyzer/config.py`. 
**Justificativa**: A decisão do grupo (#58) definiu que reduzir o código descartaria configurações já validadas e poderia quebrar implementações futuras. Optou-se por ampliar o SDD para ser compatível com o código e inserir um teste de consistência automatizado para garantir que ambos permaneçam em sincronia (onde o SDD é ajustado ao config de forma documentada neste refinamento).

---

## 9. Histórico de Versões

| Versão | Data | Alteração | Motivo | Autor |
| --- | --- | --- | --- |
| v1.0 | 2026-09-03 | Criação do documento | Especificação inicial para o Bootcamp | Ana Clara |
| v1.1 | 2026-09-08 | Correção de numerações (RN), remoção de conflito de SLA (RNF) e ajustes nos contratos de erro da API (422). | Refinamento após revisão de arquitetura | Mariana |
| v1.2 | 2026-09-12 | Ampliação das listas da seção 4.2 para parear com config.py. | Refinamento por Feedback (Issue #58) | Ana Clara |

