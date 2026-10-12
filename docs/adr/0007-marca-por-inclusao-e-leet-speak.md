# ADR-0007: Detecção de marca por inclusão no host, com normalização leet speak

**Status:** Aceita
**Data:** 2026-09-12 (RN-05 atualizada no SDD v1.2, issue #59); registrada como ADR em 2026-10-12

## Contexto

A heurística RF-10 / RN-05 deve identificar hosts que se passam por marcas monitoradas
(`paypal`, `itau`, `caixa` etc., lista em `config.MONITORED_BRANDS`). Atacantes usam duas
técnicas principais:

* incluir o nome da marca num domínio que não é dela (`paypal-secure.verify-account.top`);
* trocar letras por números parecidos (`paypa1`, `1tau`), o chamado leet speak.

Técnicas mais sofisticadas (troca de letras vizinhas, letras duplicadas, homógrafos Unicode) têm
tratamento separado ou estão fora de escopo (SDD §1.1; homógrafos ficam na RF-11).

O exemplo normativo do SDD §5.2 (`http://paypa1-secure.verify-account.top/login`, score 70)
depende de reconhecer `paypa1` como `paypal`.

## Decisão

1. Converter o host com um mapa fixo de leet speak: `0→o`, `1→l`, `3→e`, `4→a`, `5→s`, `7→t`.
2. Disparar se o **nome da marca estiver contido** no host convertido (busca por substring).
3. Não disparar se o host for o domínio oficial da marca ou um subdomínio dele.

A implementação está em `analyzer/rules/brand_impersonation.py`. Cada análise emite no máximo um
motivo `possivel_impersonacao_marca:<marca>` (RN-07).

## Alternativas Consideradas

### Igualdade exata do label

Disparar só quando um label for igual ao nome da marca (`paypal.exemplo.com`). Gera menos falsos
positivos, mas perde o caso mais comum de phishing (`paypal-secure`, `minhacaixa-login`) e o
próprio exemplo normativo do SDD.

### Fronteira de palavra (separadores `-` e `.`)

Exigir que a marca apareça cercada por início/fim de label ou hífen. Elimina casos como
`capitaurbana.com`, mas falha em `paypalsecure.com` e `caixalogin.com`, padrões reais de ataque.
Ficou como candidata à evolução.

### Distância de edição (Levenshtein) ou similaridade

Captura typosquatting genérico (`paypall`, `itaú` → `itau`), mas exige escolher um limiar, gera
resultados difíceis de explicar no campo `reasons` e amplia o escopo além do que o SDD §1.1 prevê.

### Sem normalização leet

Mais simples, mas deixaria de detectar o exemplo normativo do SDD e uma das variações mais usadas
em campanhas reais.

## Consequências

### Positivas

* Regra curta, determinística e explicável: o motivo informa qual marca foi encontrada.
* Detecta as variações mais comuns (inclusão e leet) sem lista de domínios maliciosos.
* Os domínios oficiais não são penalizados, e a allowlist (RN-03) ainda tem precedência.

### Negativas / Trade-offs

* **Falsos positivos por coincidência de letras** (issue #91), confirmados em 2026-10-12:

  ```text
  https://capitaurbana.com/  → 25, possivel_impersonacao_marca:itau
  https://caixadesom.com/    → 25, possivel_impersonacao_marca:caixa
  ```

  Sozinhos, 25 pontos resultam em `segura`. Mas o mesmo host servido por HTTP soma 35 e passa a
  `suspeita`, o que pode alarmar o usuário sem motivo real.
* Marcas com nomes curtos ou palavras comuns (`caixa`, `itau`) são as mais afetadas. Cada marca
  nova na lista aumenta a chance de colisão, então ampliar `MONITORED_BRANDS` é decisão de produto.
* O mapa leet é fixo: variações fora dele (`8→b`, `@→a`) não são normalizadas.
* Typosquatting ortográfico (`paypall`) continua sem detecção, conforme o SDD.

## Evolução da decisão

Duas opções para reduzir os falsos positivos, em ordem de custo: exigir fronteira de label/hífen
para marcas curtas, ou combinar inclusão com distância de edição. As duas mudam a RN-05 e exigem
atualizar o SDD antes do código. Enquanto isso, a limitação deve constar no SDD e ser fixada por
teste (issue #91), para que qualquer mudança futura seja deliberada.
