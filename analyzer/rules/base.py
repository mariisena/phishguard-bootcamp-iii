"""Tipo de retorno comum a todas as heurísticas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class HeuristicResult:
    triggered: bool
    reason: Optional[str] = None


def not_triggered() -> HeuristicResult:
    return HeuristicResult(triggered=False, reason=None)


def fired(reason: str) -> HeuristicResult:
    return HeuristicResult(triggered=True, reason=reason)
