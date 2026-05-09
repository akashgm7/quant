from fastapi import APIRouter
from core.store import get_signals, update_signal as store_update

router = APIRouter()

@router.get("/")
async def get_all_signals():
    return get_signals()

@router.patch("/{signal_id}")
async def patch_signal(signal_id: int, update_data: dict):
    result = store_update(signal_id, update_data)
    if result:
        return result
    return {"error": "Signal not found"}
