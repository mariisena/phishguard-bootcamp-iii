"""Normalização e validação de URLs de entrada (componente isolado — ver SPECIFICATION.md §6)."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse

from analyzer import config


class InvalidURLError(ValueError):
    """Levantada quando a URL de entrada não pode ser normalizada com segurança (RF-17)."""


@dataclass(frozen=True)
class ParsedURL:
    raw: str
    scheme: str
    host: str
    path: str
    query: str
    has_userinfo: bool
    explicit_scheme: bool


def normalize(url: object) -> ParsedURL:
    """Normaliza e valida uma URL bruta. Lança InvalidURLError em qualquer entrada inválida."""
    if not isinstance(url, str):
        raise InvalidURLError("URL inválida: esperado uma string.")

    candidate = url.strip()
    if not candidate:
        raise InvalidURLError("URL inválida: string vazia.")

    if len(candidate) > config.MAX_INPUT_LENGTH:
        raise InvalidURLError(
            f"URL inválida: excede o tamanho máximo de {config.MAX_INPUT_LENGTH} caracteres."
        )

    # Detecta esquema explícito mesmo sem "//" (ex.: "javascript:", "mailto:", "data:"), não só
    # "http://"/"https://" — do contrário esses esquemas perigosos seriam tratados como se fossem
    # um domínio comum ao receber o prefixo "http://" abaixo.
    try:
        scheme_probe = urlparse(candidate)
    except ValueError as exc:
        raise InvalidURLError(f"URL inválida: {exc}") from exc

    explicit_scheme = bool(scheme_probe.scheme)
    working = candidate if explicit_scheme else f"http://{candidate}"

    try:
        parsed = urlparse(working)
    except ValueError as exc:  # urlparse pode levantar ValueError em portas inválidas etc.
        raise InvalidURLError(f"URL inválida: {exc}") from exc

    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(f"URL inválida: esquema '{parsed.scheme}' não suportado.")

    has_userinfo = "@" in parsed.netloc

    try:
        host = parsed.hostname
    except ValueError as exc:
        raise InvalidURLError(f"URL inválida: host malformado ({exc}).") from exc

    if not host:
        raise InvalidURLError("URL inválida: host ausente.")

    return ParsedURL(
        raw=candidate,
        scheme=parsed.scheme,
        host=host.lower().rstrip("."),
        path=parsed.path or "",
        query=parsed.query or "",
        has_userinfo=has_userinfo,
        explicit_scheme=explicit_scheme,
    )


def is_ip_host(host: str) -> bool:
    """True se `host` for um literal IPv4 ou IPv6 (RF-05)."""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False
