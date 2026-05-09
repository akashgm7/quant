from fastapi import APIRouter, Query
from services.backtester import backtester

router = APIRouter()

@router.get("/run")
async def run_backtest(
    symbol: str = "BTC/USDT", 
    timeframe: str = "15m", 
    days: int = Query(30, ge=1, le=90)
):
    results = await backtester.run_backtest(symbol, timeframe, days)
    return results
