from typing import Any

from fastapi import APIRouter, Depends

from api import deps

router = APIRouter()

@router.get("/health")
def health(
) -> Any:
    """
    Health check
    """
    return {"status": "ok"}
