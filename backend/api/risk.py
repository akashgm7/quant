from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

class RiskSettings(BaseModel):
    account_balance: float = 10000.0
    risk_per_trade_percent: float = 1.0
    max_open_trades: int = 3
    max_daily_drawdown_percent: float = 5.0
    trailing_stop_activation_percent: float = 2.0

# Mock storage for settings (should be in DB)
CURRENT_SETTINGS = RiskSettings()

@router.get("/")
async def get_risk_settings():
    return CURRENT_SETTINGS

@router.post("/update")
async def update_risk_settings(settings: RiskSettings):
    global CURRENT_SETTINGS
    CURRENT_SETTINGS = settings
    return {"message": "Risk settings updated successfully", "settings": CURRENT_SETTINGS}
