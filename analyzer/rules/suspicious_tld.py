"""RF-08: TLD pertencente à lista fechada de TLDs suspeitos (SDD §4.2).

O TLD considerado é o último label do host canônico. O normalizador já entrega o host em
minúsculas e sem ponto final absoluto (N-05), portanto a comparação é direta e case-insensitive
por construção.
"""

from analyzer import config
from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "tld_suspeito"


def check(parsed: ParsedURL) -> HeuristicResult:
    tld = parsed.host.rsplit(".", 1)[-1]
    if tld in config.SUSPICIOUS_TLDS:
        return fired(REASON)
    return not_triggered()
