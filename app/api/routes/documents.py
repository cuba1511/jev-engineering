from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from typesafe_sdk import TypeSafeError

from app.api.dependencies import get_jev
from app.documents import DocumentChecker
from app.jev import Jev
from app.schemas import DocumentVerification, DocumentVerificationRequest


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/verify")
async def verify_document(
    body: DocumentVerificationRequest, jev: Annotated[Jev, Depends(get_jev)]
) -> DocumentVerification:
    try:
        return await DocumentChecker(jev).verify(body.document_text, body.expected_type, body.holder_name)
    except TypeSafeError as error:
        raise HTTPException(status_code=502, detail=f"TypeSafe error: {error}") from error
