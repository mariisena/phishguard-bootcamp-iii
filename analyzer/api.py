"""PhishGuard – camada HTTP (SDD §5.1, §5.2, §5.3).

Responsabilidades deste módulo:
  • Receber requisições HTTP.
  • Repassar a URL bruta para ``calculate_risk``.
  • Devolver a resposta serializada.

Proibições explícitas (SDD §5.1):
  • Nenhuma regra de phishing.
  • Nenhuma lógica de validação de URL.
  • HTTP 400 nunca deve ser retornado.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from analyzer.models import AnalyzeRequest, AnalyzeResponse, HealthResponse
from analyzer.scorer import calculate_risk
from analyzer.url_normalizer import InvalidURLError

# ---------------------------------------------------------------------------
# Instância da aplicação
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PhishGuard",
    version="1.0.0",
    description="Analisador de risco de phishing em tempo real.",
)

# ---------------------------------------------------------------------------
# Exception handlers – SDD §5.3
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def _validation_error_handler(request, exc: RequestValidationError) -> JSONResponse:
    """Captura erros de shape/tipo do body (Pydantic) e devolve HTTP 422.

    O handler padrão do FastAPI retornaria uma lista de erros aninhados.
    O SDD exige o formato ``{"detail": "..."}`` com uma string única, e proíbe HTTP 400.
    Aqui colapsamos todos os erros em uma mensagem legível.
    """
    messages = []
    for error in exc.errors():
        loc = " -> ".join(str(part) for part in error.get("loc", []))
        msg = error.get("msg", "valor inválido")
        messages.append(f"{loc}: {msg}" if loc else msg)

    detail = "; ".join(messages) if messages else str(exc)
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(InvalidURLError)
async def _invalid_url_handler(request, exc: InvalidURLError) -> JSONResponse:
    """Captura ``InvalidURLError`` propagada pelo engine e devolve HTTP 422.

    A lógica de *por que* a URL é inválida está inteiramente em ``url_normalizer.py``.
    Este handler apenas traduz a exceção para o formato de resposta exigido pelo SDD.
    """
    return JSONResponse(status_code=422, content={"detail": str(exc)})


# ---------------------------------------------------------------------------
# Endpoints – SDD §5.2
# ---------------------------------------------------------------------------


@app.post(
    "/api/v1/analyze",
    response_model=AnalyzeResponse,
    status_code=200,
    summary="Analisa uma URL quanto ao risco de phishing",
    tags=["analyzer"],
)
async def analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    """Recebe a URL, delega a análise ao engine e devolve o resultado.

    Não contém lógica de detecção nem de validação de URL (SDD §5.1).
    ``InvalidURLError`` é propagada livremente; o handler registrado acima
    a converte em HTTP 422.
    """
    result = calculate_risk(body.url)

    # ``AnalysisResult`` (dataclass do scorer) não carrega ``checked_at``.
    # A camada HTTP é o único lugar onde o timestamp de resposta faz sentido:
    # é aqui que a requisição foi atendida.
    return AnalyzeResponse(
        url=result.url,
        normalized_host=result.normalized_host,
        score=result.score,
        classification=result.classification,
        reasons=result.reasons,
        checked_at=datetime.now(tz=timezone.utc),
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=200,
    summary="Verificação de liveness do serviço",
    tags=["ops"],
)
async def health() -> HealthResponse:
    """Probe de liveness para load-balancers e orquestradores.

    Não acessa o engine nem dependências externas.
    """
    return HealthResponse(status="ok", service="phishguard", version="1.0.0")