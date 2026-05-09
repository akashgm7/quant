from fastapi import APIRouter
from services.external_data import external_data_service

router = APIRouter()

@router.get("/news")
async def get_market_news():
    return await external_data_service.fetch_market_news()

@router.get("/onchain")
async def get_onchain_alerts():
    return await external_data_service.fetch_onchain_alerts()
