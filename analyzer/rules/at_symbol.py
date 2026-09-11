"""RF-06: uso do caractere @ na seção de autoridade/userinfo.

O critério do SDD §4.2 restringe a regra ao trecho entre "//" e o início de path/query/fragmento:
um @ apenas no path ou na query não deve disparar. Essa distinção já é feita pelo normalizador e
exposta em `ParsedURL.has_userinfo`, portanto a heurística não faz parsing próprio da URL.
"""

from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "uso_arroba_userinfo"


def check(parsed: ParsedURL) -> HeuristicResult:
    if parsed.has_userinfo:
        return fired(REASON)
    return not_triggered()
