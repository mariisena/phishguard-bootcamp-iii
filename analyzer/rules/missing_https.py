"""RF-12: ausência de HTTPS."""

from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "sem_https"


def check(parsed: ParsedURL) -> HeuristicResult:
    if parsed.scheme != "https":
        return fired(REASON)
    return not_triggered()
