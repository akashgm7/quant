from fastapi import APIRouter
from core.store import get_scanner_state

router = APIRouter()

@router.get("/")
async def get_scanner():
    return get_scanner_state()
