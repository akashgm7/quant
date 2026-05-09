from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router
from core.websocket_manager import manager

app = FastAPI(title="QUANT-X | AI Market Signal Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from core.scanner import start_scanner
    start_scanner()

@app.get("/")
async def root():
    return {"status": "online", "message": "QUANT-X Signal Engine is running"}

@app.get("/health")
async def health():
    from core.store import get_signals, get_scanner_state
    return {
        "status": "healthy",
        "signals_in_memory": len(get_signals()),
        "pairs_scanned": len(get_scanner_state())
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.include_router(api_router, prefix="/api/v1")
