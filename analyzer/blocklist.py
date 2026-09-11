"""Checagem contra allowlist/blocklist locais de domínios (RF-15 / ADR-0003)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class DomainLists:
    allowlist: frozenset
    blocklist: frozenset


def _load_json_list(path: Path) -> list:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_domain_lists(data_dir: Path | None = None) -> DomainLists:
    data_dir = data_dir or DEFAULT_DATA_DIR
    allow = _load_json_list(data_dir / "allowlist.json")
    block = _load_json_list(data_dir / "blocklist.json")
    return DomainLists(
        allowlist=frozenset(d.lower() for d in allow),
        blocklist=frozenset(d.lower() for d in block),
    )


def _domain_matches(host: str, domain_set: frozenset) -> bool:
    host = host.lower()
    return host in domain_set or any(host.endswith(f".{domain}") for domain in domain_set)


def is_allowed(host: str, lists: DomainLists) -> bool:
    return _domain_matches(host, lists.allowlist)


def is_blocked(host: str, lists: DomainLists) -> bool:
    return _domain_matches(host, lists.blocklist)
