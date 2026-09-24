from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_jev
from app.jev import Jev


router = APIRouter(tags=["health"])


@router.get("/health")
async def health(jev: Annotated[Jev, Depends(get_jev)]) -> dict:
    return {"status": "ok", "model": jev.model}
