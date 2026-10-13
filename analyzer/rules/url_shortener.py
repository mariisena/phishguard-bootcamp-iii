"""RF-09: domínio de encurtador de URL conhecido (RN-08: sinaliza, não bloqueia).

A correspondência é por igualdade exata OU por sufixo com fronteira de ponto:
  - host == encurtador            → dispara (ex.: bit.ly)
  - host termina em "." + encurtador → dispara (ex.: www.bit.ly, m.bit.ly)
  - host termina com nome do encurtador sem ponto → NÃO dispara (ex.: notbit.ly)
  - encurtador no meio do host   → NÃO dispara (ex.: bit.ly.evil.com)
"""

from analyzer import config
from analyzer.rules.base import HeuristicResult, fired, not_triggered
from analyzer.url_normalizer import ParsedURL

REASON = "encurtador_conhecido_destino_nao_verificado"


def check(parsed: ParsedURL) -> HeuristicResult:
    host = parsed.host
    for shortener in config.URL_SHORTENERS:
        if host == shortener or host.endswith("." + shortener):
            return fired(REASON)
    return not_triggered()
