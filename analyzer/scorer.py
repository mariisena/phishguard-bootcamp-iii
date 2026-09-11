"""Orquestração da análise de risco (SDD §6 — componente `scorer.py`).

Responsabilidades deste módulo: normalizar a entrada, aplicar a precedência
allowlist → blocklist → heurísticas, agregar os pontos, aplicar RN-01 a RN-07 e montar o
`AnalysisResult`.

As regras específicas de cada heurística vivem em `analyzer/rules/*.py`. Este módulo apenas as
orquestra e não deve conter lógica de detecção própria.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from analyzer import config
from analyzer.blocklist import DomainLists, is_allowed, is_blocked, load_domain_lists
from analyzer.rules import (
    at_symbol,
    brand_impersonation,
    excessive_subdomains,
    ip_domain,
    missing_https,
    punycode_homograph,
    suspicious_keywords,
    url_length,
    url_shortener,
)
from analyzer.url_normalizer import normalize

# Ordem normativa dos motivos (SDD §4.1): host IP → @/userinfo → subdomínios → TLD → encurtador
# → impersonação → Punycode/Unicode → sem HTTPS → URL longa → palavra-chave sensível.
#
# A palavra-chave sensível NÃO entra nesta tupla: ela é condicionada pela RN-06 e por isso é
# avaliada separadamente, ao final, preservando a mesma ordem de saída.
#
# RN-07: a tupla é fixa e sem repetição, portanto cada heurística dispara no máximo uma vez.
STRUCTURAL_HEURISTICS = (
    ip_domain,
    at_symbol,
    excessive_subdomains,
    # RF-08 (TLD suspeito) entra aqui, entre subdomínios e encurtador, quando
    # `analyzer/rules/suspicious_tld.py` existir. `config.POINTS["tld_suspeito"]` já está definido.
    url_shortener,
    brand_impersonation,
    punycode_homograph,
    missing_https,
    url_length,
)

# RN-03 / RN-04: motivos das listas locais, fixados pela especificação.
REASON_ALLOWLIST = "dominio_allowlist"
REASON_BLOCKLIST = "dominio_blocklist"


@dataclass(frozen=True)
class AnalysisResult:
    url: str
    normalized_host: str
    score: int
    classification: str
    reasons: List[str]


def classify(score: int) -> str:
    """RN-02: 0–29 segura, 30–59 suspeita, 60–100 perigosa."""
    low, high = config.THRESHOLDS
    if score < low:
        return "segura"
    if score < high:
        return "suspeita"
    return "perigosa"


def _points_for(reason: str) -> int:
    """Pontos de um motivo (SDD §4.1).

    Motivos parametrizados, como `possivel_impersonacao_marca:<marca>`, usam a parte anterior
    ao ":" como chave de pontuação — a marca é apenas informativa.
    """
    key = reason.split(":", 1)[0]
    try:
        return config.POINTS[key]
    except KeyError as exc:
        raise KeyError(
            f"Motivo '{reason}' não possui pontuação em config.POINTS. "
            "Verifique se o código do motivo emitido pela heurística corresponde à Tabela 4.1 "
            "do SDD."
        ) from exc


def _result(parsed, score: int, reasons: List[str], classification: str) -> AnalysisResult:
    # SDD §5.2: `url` é a entrada original após trim; `parsed.raw` já é exatamente isso.
    return AnalysisResult(
        url=parsed.raw,
        normalized_host=parsed.host,
        score=score,
        classification=classification,
        reasons=reasons,
    )


def calculate_risk(url: str, lists: Optional[DomainLists] = None) -> AnalysisResult:
    """Calcula score, classificação e motivos de risco para uma URL.

    Propaga `InvalidURLError` (RF-17 / RN-09) quando a entrada não puder ser normalizada; a
    conversão para HTTP 422 é responsabilidade da camada de API.

    `lists` existe como ponto de injeção para os testes; quando omitido, as listas locais são
    carregadas de `blocklist.load_domain_lists()`.
    """
    parsed = normalize(url)
    lists = lists if lists is not None else load_domain_lists()

    # RN-03: allowlist tem prioridade absoluta e é avaliada antes da blocklist.
    if is_allowed(parsed.host, lists):
        return _result(parsed, config.SCORE_MIN, [REASON_ALLOWLIST], "segura")

    # RN-04: blocklist força score máximo e classificação perigosa.
    if is_blocked(parsed.host, lists):
        return _result(parsed, config.SCORE_MAX, [REASON_BLOCKLIST], "perigosa")

    reasons: List[str] = []
    score = 0

    for module in STRUCTURAL_HEURISTICS:
        result = module.check(parsed)
        if result.triggered:
            reasons.append(result.reason)
            score += _points_for(result.reason)

    # RN-06: a palavra-chave sensível só pontua se ao menos uma heurística RF-05 a RF-13 tiver
    # disparado. Múltiplas ocorrências não acumulam — `check` dispara no máximo uma vez.
    keyword_result = suspicious_keywords.check(parsed)
    if keyword_result.triggered and reasons:
        reasons.append(keyword_result.reason)
        score += _points_for(keyword_result.reason)

    # RN-01: clamp aplicado depois de toda a agregação, inclusive do bônus da RN-06.
    score = max(config.SCORE_MIN, min(score, config.SCORE_MAX))

    return _result(parsed, score, reasons, classify(score))
