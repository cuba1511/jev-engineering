from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    ticket_text: str = Field(min_length=1)


class TicketTriage(BaseModel):
    category: str
    category_confidence: float
    bug_severity: float
    refund_requested: float
    frustration: float


class Usage(BaseModel):
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: float | None
    latency_seconds: float


class TriageResult(BaseModel):
    model: str
    triage: TicketTriage
    usage: Usage
