"""RF-11: domínio em Punycode (xn--) ou contendo caracteres não-ASCII (ataque homograph)."""

from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "punycode_ou_unicode_suspeito"


def check(parsed: ParsedURL) -> HeuristicResult:
    # SDD §4.2: dispara se o host original possuir qualquer caractere não ASCII...
    if not parsed.host_original.isascii():
        return fired(REASON)

    # ...ou se a forma canônica IDNA contiver label iniciado por xn--.
    if any(label.startswith("xn--") for label in parsed.host.split(".")):
        return fired(REASON)

    return not_triggered()
