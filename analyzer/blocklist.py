"""Listas locais de domínios confiáveis e bloqueados (RF-15 / ADR-0003).

As listas vêm de `data/allowlist.json` e `data/blocklist.json`, são carregadas uma única vez por
processo e tratadas como configuração imutável durante a execução (ADR-0003).

As consultas usam **correspondência exata** do host canônico sem o prefixo `www.`
(RF-15, RN-03, RN-04, N-07). Um subdomínio de um item da lista não corresponde ao item.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"

_WWW_PREFIX = "www."


class InvalidDomainListError(ValueError):
    """Levantada quando um arquivo de lista local não está no formato esperado."""


@dataclass(frozen=True)
class DomainLists:
    allowlist: frozenset
    blocklist: frozenset


def canonical_for_lookup(host: str) -> str:
    """Forma do host usada nas consultas às listas.

    N-07: o prefixo `www.` é removido **apenas** para a consulta; o `normalized_host` devolvido
    pela API preserva o `www.` quando ele faz parte do host de entrada.
    """
    host = host.strip().lower().rstrip(".")
    if host.startswith(_WWW_PREFIX):
        host = host[len(_WWW_PREFIX):]
    return host


def _load_json_list(path: Path) -> List[str]:
    """Lê um arquivo de lista. Arquivo ausente equivale a lista vazia."""
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as fh:
        try:
            conteudo = json.load(fh)
        except json.JSONDecodeError as exc:
            raise InvalidDomainListError(f"{path.name}: JSON inválido ({exc}).") from exc

    if not isinstance(conteudo, list):
        raise InvalidDomainListError(f"{path.name}: esperado um array JSON de domínios.")

    for item in conteudo:
        if not isinstance(item, str):
            raise InvalidDomainListError(f"{path.name}: item {item!r} não é uma string.")

    return conteudo


@lru_cache(maxsize=None)
def load_domain_lists(data_dir: Optional[Path] = None) -> DomainLists:
    """Carrega as listas locais.

    O resultado é memoizado por diretório: os arquivos são lidos uma única vez por processo,
    conforme ADR-0003. Use `load_domain_lists.cache_clear()` em testes que alterem os arquivos.
    """
    data_dir = data_dir or DEFAULT_DATA_DIR
    return DomainLists(
        allowlist=frozenset(
            canonical_for_lookup(d) for d in _load_json_list(data_dir / "allowlist.json")
        ),
        blocklist=frozenset(
            canonical_for_lookup(d) for d in _load_json_list(data_dir / "blocklist.json")
        ),
    )


def is_allowed(host: str, lists: DomainLists) -> bool:
    """RN-03: correspondência exata do host canônico contra a allowlist."""
    return canonical_for_lookup(host) in lists.allowlist


def is_blocked(host: str, lists: DomainLists) -> bool:
    """RN-04: correspondência exata do host canônico contra a blocklist."""
    return canonical_for_lookup(host) in lists.blocklist
