# ADR-0006: Contagem de subdomínios por aproximação, sem Public Suffix List

**Status:** Aceita
**Data:** 2026-09-08 (critério definido no SDD v1.1); registrada como ADR em 2026-10-12

## Contexto

A heurística RF-07 pontua URLs com "excesso de subdomínios", um padrão comum em phishing
(`login.conta.seguranca.banco.exemplo.com`). Para contar subdomínios é preciso saber onde termina
o **domínio registrável**. Em `banco.com.br`, o sufixo público é `com.br` (dois labels); em
`exemplo.com`, é só `com`.

A forma correta de descobrir isso é a **Public Suffix List (PSL)**, mantida pela Mozilla, com
milhares de sufixos. Usá-la, porém, entra em conflito com outras decisões do projeto:

* a análise precisa ser local e determinística (RNF-02, ADR-0002);
* o SDD §1.1 coloca o uso de PSL externa fora de escopo nesta entrega;
* a lista muda com o tempo, então o resultado da RF-07 dependeria da versão da lista usada.

## Decisão

Tratar **sempre os dois últimos labels** do host como domínio-base e contar como subdomínio todo
label anterior a eles. A heurística dispara quando há **mais de três** subdomínios
(`config.MAX_SUBDOMAIN_LEVELS = 3`), conforme o critério do SDD §4.2.

```text
a.b.c.example.com     → 3 subdomínios → não dispara
a.b.c.d.example.com   → 4 subdomínios → dispara (15 pontos)
```

Hosts que são IP não passam por essa contagem (são tratados pela RF-05).

## Alternativas Consideradas

### Public Suffix List embarcada no repositório

Copiar um snapshot da PSL para `data/` manteria a análise local. Foi rejeitada nesta entrega
porque:

* acrescenta um arquivo grande que precisa de atualização periódica e de um critério para isso;
* exige parser próprio das regras da PSL (curingas `*.` e exceções `!`), ou uma dependência nova;
* o ganho fica restrito a um único requisito de 15 pontos.

### Biblioteca `tldextract` ou `publicsuffix2`

Resolve o problema com pouco código, mas por padrão `tldextract` baixa a PSL na primeira execução,
o que viola a regra de ausência de rede. Configurá-la para modo offline volta ao custo de manter
um snapshot.

### Lista curta de sufixos compostos em `config.py`

Por exemplo, `{"com.br", "gov.br", "co.uk"}`. É barata, mas cria uma terceira regra
(nem "dois últimos labels", nem PSL) que precisaria de manutenção manual e de decisão sobre
quais sufixos incluir. Ficou como possível evolução.

## Consequências

### Positivas

* Regra simples, local e determinística: o mesmo host sempre dá o mesmo resultado.
* Fácil de explicar e de testar com casos de borda exatos (3 versus 4 subdomínios).
* Nenhuma dependência nova nem arquivo de dados a manter.

### Negativas / Trade-offs

* **Falso positivo em sufixos de dois níveis**, como `.com.br`, `.gov.br` e `.co.uk`. O label
  registrável (`banco`) é contado como subdomínio, então esses hosts disparam com um subdomínio a
  menos. Verificado em 2026-10-12:

  ```text
  https://a.b.c.banco.com.br/   → 15, subdominios_excessivos  (3 subdomínios reais)
  https://a.b.c.example.com/    → 0                            (3 subdomínios reais)
  ```

  Para um serviço usado no Brasil, `.com.br` e `.gov.br` são comuns, então o efeito não é
  marginal. Isoladamente, 15 pontos ainda resultam em `segura`; somados a outro sinal, podem levar
  a `suspeita`.
* A regra mede quantidade de labels, não intenção: um ataque com poucos subdomínios
  (`login.paypal-seguro.com`) não é pego por ela e depende das outras heurísticas.
* A limitação precisa estar documentada para não ser confundida com bug (SDD §4.2 já cita a
  aproximação).

## Evolução da decisão

Substituir a aproximação por uma PSL embarcada e versionada, ou por uma lista de sufixos compostos
em `config.py`, caso a taxa de falsos positivos em domínios `.br` se mostre relevante. A mudança
altera o comportamento da RF-07 e, portanto, exige atualizar primeiro o SDD §1.1 e §4.2 e os
testes de `tests/test_excessive_subdomains.py`.
