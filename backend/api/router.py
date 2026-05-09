from fastapi import APIRouter

from api.signals import router as signals_router
from api.scanner import router as scanner_router
from api.analytics import router as analytics_router
from api.risk import router as risk_router
from api.ai import router as ai_router
from api.backtest import router as backtest_router
from api.external import router as external_router
from api.history import router as history_router

api_router = APIRouter()

api_router.include_router(signals_router, prefix="/signals", tags=["signals"])
api_router.include_router(scanner_router, prefix="/scanner", tags=["scanner"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(risk_router, prefix="/risk", tags=["risk"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
api_router.include_router(external_router, prefix="/external", tags=["external"])
api_router.include_router(history_router, prefix="/history", tags=["history"])
