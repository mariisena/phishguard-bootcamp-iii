"""RF-10 / RN-05: possível typosquatting/impersonação de marca monitorada.

Aplica uma normalização simples de "leet speak" (0→o, 1→l, 3→e, 4→a, 5→s, 7→t) antes de procurar
o nome da marca no host, para capturar variações comuns como "paypa1" → "paypal". Só dispara se o
host não for um domínio oficial da marca (RN-05).
"""

from analyzer import config
from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "possivel_impersonacao_marca"

_LEET_MAP = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t"})


def _is_official_domain(host: str, official_domains: set) -> bool:
    return any(host == official or host.endswith(f".{official}") for official in official_domains)


def check(parsed: ParsedURL) -> HeuristicResult:
    normalized_host = parsed.host.translate(_LEET_MAP)

    for brand, official_domains in config.MONITORED_BRANDS.items():
        if brand not in normalized_host:
            continue
        if _is_official_domain(parsed.host, official_domains):
            continue  # é o domínio oficial da própria marca — não é impersonação (RN-05)
        return fired(f"{REASON}:{brand}")

    return not_triggered()
