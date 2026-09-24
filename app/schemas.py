from typing import Literal

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


DocumentType = Literal["payslip", "id_document", "rental_contract", "invoice", "other"]
CheckStatus = Literal["pass", "fail", "uncertain"]


class DocumentVerificationRequest(BaseModel):
    document_text: str = Field(min_length=1)
    expected_type: DocumentType
    holder_name: str = Field(min_length=1)


class CheckResult(BaseModel):
    name: str
    status: CheckStatus
    probability: float
    detail: str


class DocumentVerification(BaseModel):
    model: str
    status: Literal["approved", "needs_review", "rejected"]
    detected_type: str
    detected_type_confidence: float
    checks: list[CheckResult]
    usage: Usage
