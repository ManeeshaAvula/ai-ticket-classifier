"""Pydantic request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Ticket text to classify")


class BatchClassifyRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=100)

    def cleaned_texts(self) -> list[str]:
        cleaned = [t.strip() for t in self.texts]
        if any(not t for t in cleaned):
            raise ValueError("Batch items must not be empty strings")
        return cleaned


class TicketOut(BaseModel):
    id: int
    text: str
    label: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassificationOut(BaseModel):
    """A prediction that has not necessarily been stored (batch results)."""

    text: str
    label: str
    confidence: float


class BatchClassifyResponse(BaseModel):
    results: list[TicketOut]


class StatsResponse(BaseModel):
    total: int
    counts: dict[str, int]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
