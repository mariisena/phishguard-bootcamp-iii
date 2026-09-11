"""RF-11: domínio em Punycode (xn--) ou contendo caracteres não-ASCII (ataque homograph)."""

from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "punycode_ou_unicode_suspeito"


def check(parsed: ParsedURL) -> HeuristicResult:
    labels = parsed.host.split(".")
    if any(label.startswith("xn--") for label in labels):
        return fired(REASON)

    try:
        parsed.host.encode("ascii")
    except UnicodeEncodeError:
        return fired(REASON)

    return not_triggered()
