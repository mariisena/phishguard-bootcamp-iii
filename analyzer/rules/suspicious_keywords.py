"""RF-14: palavra-chave sensível no path ou na query.

Esta heurística apenas detecta a presença da palavra-chave. A regra de que ela só soma pontos
quando outra heurística (RF-05 a RF-13) também disparou — RN-06 — é responsabilidade do `scorer`,
não desta função, o que a mantém pura e de responsabilidade única.

RN-07: múltiplas palavras ou múltiplas ocorrências não acumulam; a heurística dispara uma só vez.
"""

from analyzer import config
from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "palavra_chave_sensivel_no_path_query"


def check(parsed: ParsedURL) -> HeuristicResult:
    # RF-14: busca case-insensitive restrita a path e query. O fragmento não participa da
    # pontuação e já foi separado pelo normalizador.
    alvo = f"{parsed.path} {parsed.query}".lower()
    if any(keyword in alvo for keyword in config.SENSITIVE_KEYWORDS):
        return fired(REASON)
    return not_triggered()
