"""Contratos de request/response da API (ver docs/SPECIFICATION.md §5)."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)


class AnalyzeResponse(BaseModel):
    url: str
    normalized_host: str
    score: int
    classification: str
    reasons: List[str]
    checked_at: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
