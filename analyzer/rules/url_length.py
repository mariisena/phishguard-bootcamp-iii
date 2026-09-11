"""RF-13: URL anormalmente longa."""

from analyzer import config
from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "url_muito_longa"


def check(parsed: ParsedURL) -> HeuristicResult:
    if len(parsed.raw) > config.MAX_URL_LENGTH:
        return fired(REASON)
    return not_triggered()
