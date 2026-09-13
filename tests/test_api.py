"""Testes da camada HTTP do PhishGuard (analyzer/api.py).

Estratégia de isolamento
------------------------
``calculate_risk`` depende de módulos internos do pacote (``config``, ``blocklist``,
``rules/*``) que não fazem parte da camada HTTP e podem não estar disponíveis no CI.
Por isso, *todos* os testes mockam ``analyzer.api.calculate_risk`` via
``unittest.mock.patch``, garantindo que apenas a camada HTTP seja exercida aqui.

Cenários cobertos (SDD §5.2 – §5.3)
-------------------------------------
    ✓ POST /api/v1/analyze – 200 com payload válido
    ✓ POST /api/v1/analyze – resposta contém todos os campos de AnalyzeResponse
    ✓ POST /api/v1/analyze – ``checked_at`` é injetado pela camada HTTP (não vem do engine)
    ✓ POST /api/v1/analyze – URL é repassada ao engine sem modificação
    ✓ POST /api/v1/analyze – 422 body ausente
    ✓ POST /api/v1/analyze – 422 objeto JSON vazio (campo ``url`` ausente)
    ✓ POST /api/v1/analyze – 422 ``url`` com string vazia (viola min_length=1)
    ✓ POST /api/v1/analyze – 422 ``url`` excede max_length=2048
    ✓ POST /api/v1/analyze – 422 quando engine lança ``InvalidURLError``
    ✓ POST /api/v1/analyze – corpo de todo 422 é ``{"detail": "<str>"}``
    ✓ POST /api/v1/analyze – HTTP 400 NUNCA é retornado
    ✓ GET  /health         – 200 com campos status, service e version
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from analyzer.api import app
from analyzer.url_normalizer import InvalidURLError

client = TestClient(app, raise_server_exceptions=False)

# ---------------------------------------------------------------------------
# Fixtures e fábrica de AnalysisResult fake
# ---------------------------------------------------------------------------

_ANALYZE = "/api/v1/analyze"
_HEALTH = "/health"


@dataclass(frozen=True)
class _FakeAnalysisResult:
    """Imita ``AnalysisResult`` do scorer sem importar o módulo real."""

    url: str
    normalized_host: str
    score: int
    classification: str
    reasons: List[str]


def _make_result(
    url: str = "https://example.com",
    host: str = "example.com",
    score: int = 0,
    classification: str = "segura",
    reasons: List[str] | None = None,
) -> _FakeAnalysisResult:
    return _FakeAnalysisResult(
        url=url,
        normalized_host=host,
        score=score,
        classification=classification,
        reasons=reasons or [],
    )


def _post(url: str, **kwargs):
    return client.post(_ANALYZE, json={"url": url}, **kwargs)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_returns_200(self):
        assert client.get(_HEALTH).status_code == 200

    def test_body_status_ok(self):
        assert client.get(_HEALTH).json()["status"] == "ok"

    def test_body_has_service(self):
        body = client.get(_HEALTH).json()
        assert "service" in body
        assert isinstance(body["service"], str)
        assert body["service"] != ""

    def test_body_has_version(self):
        body = client.get(_HEALTH).json()
        assert "version" in body
        assert isinstance(body["version"], str)
        assert body["version"] != ""


# ---------------------------------------------------------------------------
# POST /api/v1/analyze – cenários de sucesso (200)
# ---------------------------------------------------------------------------


class TestAnalyzeSuccess:
    @patch("analyzer.api.calculate_risk")
    def test_returns_200(self, mock_cr):
        mock_cr.return_value = _make_result()
        assert _post("https://example.com").status_code == 200

    @patch("analyzer.api.calculate_risk")
    def test_response_has_all_fields(self, mock_cr):
        mock_cr.return_value = _make_result()
        body = _post("https://example.com").json()
        for field in ("url", "normalized_host", "score", "classification", "reasons", "checked_at"):
            assert field in body, f"Campo ausente: {field}"

    @patch("analyzer.api.calculate_risk")
    def test_url_field_matches_engine_output(self, mock_cr):
        """``url`` da resposta deve ser a URL devolvida pelo engine (após trim), não a entrada bruta."""
        mock_cr.return_value = _make_result(url="https://example.com")
        body = _post("https://example.com").json()
        assert body["url"] == "https://example.com"

    @patch("analyzer.api.calculate_risk")
    def test_normalized_host_from_engine(self, mock_cr):
        mock_cr.return_value = _make_result(host="example.com")
        body = _post("https://example.com").json()
        assert body["normalized_host"] == "example.com"

    @patch("analyzer.api.calculate_risk")
    def test_score_is_int(self, mock_cr):
        mock_cr.return_value = _make_result(score=42)
        body = _post("https://example.com").json()
        assert body["score"] == 42

    @patch("analyzer.api.calculate_risk")
    def test_classification_forwarded(self, mock_cr):
        mock_cr.return_value = _make_result(score=75, classification="perigosa")
        body = _post("https://example.com").json()
        assert body["classification"] == "perigosa"

    @patch("analyzer.api.calculate_risk")
    def test_reasons_is_list(self, mock_cr):
        mock_cr.return_value = _make_result(reasons=["host_ip", "sem_https"])
        body = _post("https://example.com").json()
        assert body["reasons"] == ["host_ip", "sem_https"]

    @patch("analyzer.api.calculate_risk")
    def test_checked_at_is_injected_by_api_layer(self, mock_cr):
        """``checked_at`` não existe em ``AnalysisResult``; a API deve criá-lo."""
        mock_cr.return_value = _make_result()
        before = datetime.now(tz=timezone.utc)
        body = _post("https://example.com").json()
        after = datetime.now(tz=timezone.utc)

        checked_at = datetime.fromisoformat(body["checked_at"])
        assert before <= checked_at <= after

    @patch("analyzer.api.calculate_risk")
    def test_url_is_passed_verbatim_to_engine(self, mock_cr):
        """A API não deve pré-processar a URL antes de repassar ao engine."""
        mock_cr.return_value = _make_result(url="https://example.com/path?q=1")
        _post("https://example.com/path?q=1")
        mock_cr.assert_called_once_with("https://example.com/path?q=1")

    @patch("analyzer.api.calculate_risk")
    def test_suspecting_url_returns_200(self, mock_cr):
        mock_cr.return_value = _make_result(score=45, classification="suspeita")
        assert _post("https://suspicious-site.com").status_code == 200

    @patch("analyzer.api.calculate_risk")
    def test_dangerous_url_returns_200(self, mock_cr):
        """URLs perigosas são informadas na resposta, não rejeitadas com 4xx."""
        mock_cr.return_value = _make_result(score=100, classification="perigosa")
        assert _post("https://phishing.example.com").status_code == 200


# ---------------------------------------------------------------------------
# POST /api/v1/analyze – cenários de erro 422
# ---------------------------------------------------------------------------


class TestAnalyze422Shape:
    """Garante que *todo* 422 tem formato ``{"detail": "<str não vazia>"}``."""

    def _assert_422_shape(self, response):
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body, "Resposta 422 deve conter campo 'detail'"
        assert isinstance(body["detail"], str), "'detail' deve ser string"
        assert len(body["detail"]) > 0, "'detail' não pode ser string vazia"
        # SDD proíbe HTTP 400 — verificação defensiva extra
        assert response.status_code != 400

    def test_missing_body(self):
        self._assert_422_shape(client.post(_ANALYZE))

    def test_empty_json_object(self):
        self._assert_422_shape(client.post(_ANALYZE, json={}))

    def test_empty_string_url(self):
        self._assert_422_shape(client.post(_ANALYZE, json={"url": ""}))

    def test_url_exceeds_max_length(self):
        self._assert_422_shape(client.post(_ANALYZE, json={"url": "https://x.com/" + "a" * 2050}))

    def test_wrong_content_type(self):
        self._assert_422_shape(
            client.post(
                _ANALYZE,
                content="url=https://example.com",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        )

    @patch("analyzer.api.calculate_risk", side_effect=InvalidURLError("URL inválida: esquema 'ftp' não suportado."))
    def test_invalid_url_error_from_engine(self, _):
        self._assert_422_shape(client.post(_ANALYZE, json={"url": "ftp://files.example.com"}))

    @patch("analyzer.api.calculate_risk", side_effect=InvalidURLError("URL inválida: host ausente."))
    def test_invalid_url_no_host(self, _):
        self._assert_422_shape(client.post(_ANALYZE, json={"url": "https:///sem-host"}))

    @patch("analyzer.api.calculate_risk", side_effect=InvalidURLError("URL inválida: string vazia."))
    def test_invalid_url_empty_after_strip(self, _):
        self._assert_422_shape(client.post(_ANALYZE, json={"url": "   "}))

    @patch("analyzer.api.calculate_risk", side_effect=InvalidURLError("URL inválida: host contém espaços."))
    def test_invalid_url_host_with_spaces(self, _):
        self._assert_422_shape(client.post(_ANALYZE, json={"url": "https://bad host.com"}))


class TestAnalyze400NeverReturned:
    """HTTP 400 é proibido pelo SDD – validado separadamente para cada caso de erro."""

    @pytest.mark.parametrize(
        "payload",
        [
            None,                           # body ausente
            {},                             # campo url ausente
            {"url": ""},                    # url vazia (viola min_length)
            {"url": "x" * 2049},           # url longa (viola max_length=2048, sem scheme)
        ],
    )
    def test_pydantic_errors_never_return_400(self, payload):
        if payload is None:
            response = client.post(_ANALYZE)
        else:
            response = client.post(_ANALYZE, json=payload)
        assert response.status_code != 400

    @pytest.mark.parametrize(
        "error_msg",
        [
            "URL inválida: esquema 'ftp' não suportado.",
            "URL inválida: host ausente.",
            "URL inválida: string vazia.",
            "URL inválida: informe uma URL absoluta com esquema http ou https e host válido.",
        ],
    )
    def test_invalid_url_error_never_returns_400(self, error_msg):
        with patch("analyzer.api.calculate_risk", side_effect=InvalidURLError(error_msg)):
            response = client.post(_ANALYZE, json={"url": "qualquer-coisa"})
        assert response.status_code != 400


# ---------------------------------------------------------------------------
# Verificação de pureza: api.py não deve importar módulos de heurísticas
# ---------------------------------------------------------------------------


class TestApiPurity:
    def test_api_module_does_not_import_rules(self):
        """A camada HTTP não deve depender de nenhum módulo de heurísticas."""
        import analyzer.api as api_module
        import sys

        rule_modules = [name for name in sys.modules if "analyzer.rules" in name]
        # Se nenhum módulo de regra foi importado *por causa* da api, a camada está pura.
        # (Módulos já presentes no sys.modules antes da importação de api são ignorados.)
        api_source = api_module.__file__
        with open(api_source) as f:
            source = f.read()
        assert "rules" not in source, (
            "api.py não deve importar nem referenciar módulos de heurísticas diretamente."
        )

    def test_api_module_does_not_import_blocklist(self):
        import analyzer.api as api_module

        with open(api_module.__file__) as f:
            source = f.read()
        assert "blocklist" not in source, (
            "api.py não deve importar blocklist — isso é responsabilidade do scorer."
        )

    def test_api_module_does_not_import_config(self):
        import analyzer.api as api_module

        with open(api_module.__file__) as f:
            source = f.read()
        assert "from analyzer import config" not in source and "import config" not in source, (
            "api.py não deve importar config — limites e thresholds são responsabilidade do engine."
        )