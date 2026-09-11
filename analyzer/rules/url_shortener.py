"""RF-09: domínio de encurtador de URL conhecido (RN-08: sinaliza, não bloqueia)."""

from analyzer import config
from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "encurtador_conhecido_destino_nao_verificado"


def check(parsed: ParsedURL) -> HeuristicResult:
    if parsed.host in config.URL_SHORTENERS:
        return fired(REASON)
    return not_triggered()
