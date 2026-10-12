---
paths:
  - "analyzer/**/*.py"
---

# Regras de código (pacote `analyzer/`)

Complementa as seções "Convenções de código", "Estrutura das heurísticas", "Constantes de negócio"
e "Normalização de URLs" do `CLAUDE.md`. Aqui ficam só os pontos específicos que já causaram erro
neste repositório (ver `docs/registro_correcoes/`).

## Pacote e imports

- O pacote se chama `analyzer`. **Não existe** pacote `phishguard` instalável: `import phishguard...`
  ou `phishguard.api:app` é sempre erro (já aconteceu em `url_shortener.py`, `userinfo_symbol.py` e
  `docker-compose.yml`).
- Antes de importar algo, confirme que o módulo existe no repositório ou no `requirements.txt`.
  Não adicione dependência nova sem decisão humana.
- Ordem dos imports: biblioteca padrão, terceiros, `analyzer.*`. Formatação com `black`.

## Heurísticas (`analyzer/rules/`)

- Uma heurística por arquivo, com `check(parsed: ParsedURL) -> HeuristicResult`.
- Use `fired(REASON)` e `not_triggered()` de `analyzer/rules/base.py`. A heurística **não** devolve
  pontos: a pontuação é do `scorer.py`, via `config.POINTS`.
- O código de motivo (`REASON`) deve ser exatamente o da Tabela 4.1 do SDD. Não invente códigos
  (`ip_literal_no_host`, `arroba_na_url` e similares já foram rejeitados).
- Nada de `urlparse`, `split("/")` ou regex sobre a URL crua dentro de uma heurística: use os campos
  do `ParsedURL` (`normalized_host`, `path`, `query`, `has_userinfo`, `host_original`...).
  Se faltar um campo, ele entra no `url_normalizer.py`, com teste e respaldo no SDD §5.4.
- Sem I/O, rede, relógio, aleatoriedade ou estado global mutável.
- Nova heurística entra na tupla do `scorer.py` **na posição da ordem normativa do §4.1**, nunca
  ao final por conveniência.

## Constantes

- Pesos, limiares, listas e `SCORE_MIN`/`SCORE_MAX` ficam só em `analyzer/config.py`.
  Não copie uma lista para dentro de uma heurística nem escreva `<= 29`, `>= 60` ou `100` soltos.
- Alterar valor em `config.py` é decisão de produto: pare e pergunte (ver "O que o agente NÃO deve
  fazer sem confirmação humana" no `CLAUDE.md`). O `tests/test_config_consistency.py` compara o
  `config.py` com o SDD e vai falhar se só um dos lados mudar.

## Erros

- Entrada inválida vira `InvalidURLError`, levantada no normalizador.
- Proibido `except Exception: pass` ou `except: ...` que esconda falha. Num detector de phishing,
  uma exceção engolida vira um resultado `segura` falso.
- Capture só a exceção específica que você sabe tratar e converta para o erro previsto no SDD.

## Scorer

- Ordem fixa: normalizar → allowlist (RN-03) → blocklist (RN-04) → heurísticas → RN-06 → soma →
  clamp (RN-01) **depois** de toda a agregação → classificação via `config.THRESHOLDS`.
- O resultado não pode ter campos variáveis (timestamp, UUID, ordem de `set`). Ver RNF-02.
