from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router
from core.websocket_manager import manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="QUANT-X | AI Market Signal Engine")

# Fully permissive CORS for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
async def startup_event():
    from core.scanner import start_scanner
    logger.info("🚀 API is starting up...")
    start_scanner()

@app.get("/")
async def root():
    return {"status": "online", "message": "QUANT-X Signal Engine is running"}

@app.get("/health")
async def health():
    from core.store import get_signals, get_scanner_state
    state = get_scanner_state()
    return {
        "status": "healthy",
        "scanner_active": len(state) > 0,
        "signals_detected": len(get_signals()),
        "pairs_scanned": [s['symbol'] for s in state]
    }

@app.get("/test-telegram")
async def test_telegram():
    from services.telegram_bot import telegram_service
    try:
        await telegram_service.send_signal({
            "symbol": "SYSTEM",
            "direction": "ONLINE",
            "entry": 1.0,
            "stop_loss": 0.0,
            "take_profit_1": 2.0,
            "take_profit_2": 3.0,
            "risk_reward": "N/A",
            "confidence": 100,
            "reasons": ["Scanner is Live", "Multi-Exchange Logic Active", "Connection Verified"]
        })
        return {"status": "success", "message": "Test signal sent to Telegram"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.include_router(api_router, prefix="/api/v1")
