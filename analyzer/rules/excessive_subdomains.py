"""RF-07: domínio com número excessivo de subdomínios."""

from analyzer import config
from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "subdominios_excessivos"


def check(parsed: ParsedURL) -> HeuristicResult:
    labels = [label for label in parsed.host.split(".") if label]
    subdomain_levels = max(0, len(labels) - 2)
    if subdomain_levels > config.MAX_SUBDOMAIN_LEVELS:
        return fired(REASON)
    return not_triggered()
