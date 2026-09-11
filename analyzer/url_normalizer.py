"""Normalização e validação de URLs de entrada (SDD §5.4 — regras N-01 a N-09).

Este é o único componente autorizado a fazer parsing de URL. As heurísticas trabalham sobre o
`ParsedURL` produzido aqui e nunca sobre a string bruta.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse

from analyzer import config

ALLOWED_SCHEMES = ("http", "https")


class InvalidURLError(ValueError):
    """Levantada quando a URL de entrada não pode ser normalizada com segurança (RF-17)."""


@dataclass(frozen=True)
class ParsedURL:
    """Representação estruturada e já normalizada de uma URL.

    `host` é a forma canônica IDNA ASCII usada em `normalized_host` e nas consultas às listas.
    `host_original` preserva o host antes da conversão IDNA, porque a RF-11 precisa saber se a
    entrada trazia caracteres não ASCII (N-06).
    """

    raw: str
    scheme: str
    host: str
    host_original: str
    path: str
    query: str
    path_lower: str
    query_lower: str
    has_userinfo: bool


def _canonical_host(host: str) -> str:
    """N-05: host em minúsculas, sem o ponto final absoluto e com labels não vazios."""
    host = host.lower()

    # N-05 fala do ponto final *absoluto* — apenas um. Pontos extras deixam um label vazio,
    # que é rejeitado logo abaixo.
    if host.endswith("."):
        host = host[:-1]

    if not host:
        raise InvalidURLError("URL inválida: host ausente.")

    # RF-04 exige host válido; espaço em branco no host é malformado por definição.
    if any(caractere.isspace() for caractere in host):
        raise InvalidURLError("URL inválida: host contém espaços.")

    if any(not label for label in host.split(".")):
        raise InvalidURLError(f"URL inválida: host '{host}' contém label vazio.")

    return host


def _to_idna_ascii(host: str) -> str:
    """N-06: converte hosts IDN/Unicode para a forma IDNA ASCII.

    Hosts já ASCII são devolvidos inalterados: o codec `idna` da stdlib rejeita labels ASCII com
    mais de 63 caracteres, e a especificação não manda invalidar esse caso.
    """
    if host.isascii():
        return host

    try:
        return host.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise InvalidURLError(f"URL inválida: host IDN não conversível ({exc}).") from exc


def normalize(url: object) -> ParsedURL:
    """Normaliza e valida uma URL bruta. Lança `InvalidURLError` em qualquer entrada inválida."""
    # N-01: a entrada deve ser string; espaços externos saem antes da validação.
    if not isinstance(url, str):
        raise InvalidURLError("URL inválida: esperado uma string.")

    candidate = url.strip()

    # N-02: após o trim, o comprimento deve estar entre 1 e MAX_INPUT_LENGTH.
    if not candidate:
        raise InvalidURLError("URL inválida: string vazia.")
    if len(candidate) > config.MAX_INPUT_LENGTH:
        raise InvalidURLError(
            f"URL inválida: excede o tamanho máximo de {config.MAX_INPUT_LENGTH} caracteres."
        )

    try:
        parsed = urlparse(candidate)
    except ValueError as exc:
        raise InvalidURLError(f"URL inválida: {exc}") from exc

    # N-03 / RF-04: o esquema é obrigatório e a URL deve ser absoluta. Entradas como
    # "www.exemplo.com" não recebem esquema por conta própria — são rejeitadas.
    # `urlparse` já devolve o esquema em minúsculas, atendendo à comparação case-insensitive.
    if not parsed.scheme:
        raise InvalidURLError(
            "URL inválida: informe uma URL absoluta com esquema http ou https e host válido."
        )
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise InvalidURLError(f"URL inválida: esquema '{parsed.scheme}' não suportado.")

    # N-09: userinfo sintaticamente válido não invalida a URL; a presença do @ vira sinal (RF-06).
    has_userinfo = "@" in parsed.netloc

    try:
        host = parsed.hostname
        parsed.port  # valida a porta, que não faz parte do host canônico (N-05)
    except ValueError as exc:
        raise InvalidURLError(f"URL inválida: autoridade malformada ({exc}).") from exc

    # N-04: o host é obrigatório.
    if not host:
        raise InvalidURLError("URL inválida: host ausente.")

    host_original = _canonical_host(host)

    # N-08: path e query preservados, com uma visão em minúsculas para comparações
    # case-insensitive. O fragmento é descartado por `urlparse` e não participa da pontuação.
    path = parsed.path or ""
    query = parsed.query or ""

    return ParsedURL(
        raw=candidate,
        scheme=parsed.scheme,
        host=_to_idna_ascii(host_original),
        host_original=host_original,
        path=path,
        query=query,
        path_lower=path.lower(),
        query_lower=query.lower(),
        has_userinfo=has_userinfo,
    )


def is_ip_host(host: str) -> bool:
    """True se `host` for um literal IPv4 ou IPv6 (RF-05)."""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False
