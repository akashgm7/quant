import asyncio
import logging
from services.market_data import market_data_service
from services.signal_engine import signal_engine
from services.telegram_bot import telegram_service
from core.websocket_manager import manager
from core.store import add_signal, set_scanner_state, get_scanner_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
TIMEFRAMES = ["5m", "15m"]

async def market_scanner():
    logger.info("🚀 QUANT-X Scalping Scanner started.")
    
    # Initialize state with symbols so they appear immediately on the dashboard
    initial_state = [{"symbol": p, "bias": "LOADING", "volatility": "-", "rsi": 0, "price": 0, "change_24h": 0} for p in PAIRS]
    set_scanner_state(initial_state)

    while True:
        try:
            current_state = get_scanner_state()
            
            for symbol in PAIRS:
                for tf in TIMEFRAMES:
                    logger.info(f"Scanning {symbol} ({tf})...")
                    df = await market_data_service.fetch_ohlcv(symbol, timeframe=tf, limit=100)
                    if df is None:
                        continue

                    # Update scanner state immediately for this symbol
                    if tf == "15m":
                        structure = await market_data_service.get_market_structure(df)
                        avg_vol = df['volume'].iloc[-20:].mean()
                        curr_vol = df['volume'].iloc[-1]
                        
                        # Find and update this symbol in the state
                        for i, item in enumerate(current_state):
                            if item["symbol"] == symbol:
                                current_state[i] = {
                                    "symbol": symbol,
                                    "bias": structure["bias"],
                                    "volatility": "High" if curr_vol > avg_vol * 1.5 else "Normal",
                                    "rsi": 50.0, # Placeholder or calculate
                                    "price": float(df['close'].iloc[-1]),
                                    "change_24h": 0.0
                                }
                                break
                        
                        # Broadcast update immediately
                        set_scanner_state(current_state)
                        await manager.broadcast({"type": "scanner_update", "data": current_state})

                    # SCALPING SIGNAL ANALYSIS
                    signal = await signal_engine.analyze_confluence(df, symbol, market_data_service)
                    if signal:
                        signal["timeframe"] = tf
                        stored = add_signal(signal)
                        await telegram_service.send_signal(stored)
                        await manager.broadcast({"type": "new_signal", "data": stored})

        except Exception as e:
            logger.error(f"Scanner loop error: {e}")

        await asyncio.sleep(30) # High-frequency refresh

def start_scanner():
    asyncio.create_task(market_scanner())
