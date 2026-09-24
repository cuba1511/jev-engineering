from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from typesafe_sdk import TypeSafeError

from app.api.dependencies import get_jev
from app.jev import Jev
from app.schemas import TriageRequest, TriageResult


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/triage")
async def triage_ticket(body: TriageRequest, jev: Annotated[Jev, Depends(get_jev)]) -> TriageResult:
    try:
        return await jev.triage(body.ticket_text)
    except TypeSafeError as error:
        raise HTTPException(status_code=502, detail=f"TypeSafe error: {error}") from error
