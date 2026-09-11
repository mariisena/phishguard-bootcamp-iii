"""RF-05: host é um endereço IP (IPv4 ou IPv6) em vez de um nome de domínio.

A detecção usa `url_normalizer.is_ip_host`, que cobre IPv4 e IPv6 conforme RF-05. Porta e
colchetes de IPv6 já foram removidos pelo normalizador, portanto a heurística não faz parsing
próprio.
"""

from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL, is_ip_host

REASON = "host_ip"


def check(parsed: ParsedURL) -> HeuristicResult:
    if is_ip_host(parsed.host):
        return fired(REASON)
    return not_triggered()
