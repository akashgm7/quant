import asyncio
import logging
from services.market_data import market_data_service
from services.signal_engine import signal_engine
from services.telegram_bot import telegram_service
from core.websocket_manager import manager
from core.store import add_signal, set_scanner_state, get_scanner_state, is_in_cooldown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]

async def market_scanner():
    logger.info("🎯 QUANT-X Fibonacci Sniper Scanner active.")
    
    # 1. IMMEDIATE INITIALIZATION
    initial_state = [{"symbol": p, "bias": "INITIALIZING", "volatility": "-", "rsi": 0, "price": 0} for p in PAIRS]
    set_scanner_state(initial_state)

    while True:
        try:
            current_state = get_scanner_state()
            
            for symbol in PAIRS:
                try:
                    # 2. CHECK COOLDOWN
                    if is_in_cooldown(symbol):
                        continue

                    # 3. MULTI-TF FETCH WITH INDIVIDUAL TIMEOUTS
                    logger.info(f"Scanning {symbol}...")
                    
                    # Fetch 15m first as it's the most critical
                    df_15m = await asyncio.wait_for(market_data_service.fetch_ohlcv(symbol, '15m', 100), timeout=10.0)
                    if df_15m is None: continue

                    # Update UI price immediately
                    for i, item in enumerate(current_state):
                        if item["symbol"] == symbol:
                            current_state[i]["price"] = float(df_15m['close'].iloc[-1])
                            current_state[i]["bias"] = "FETCHING TREND..."
                            break
                    set_scanner_state(current_state)

                    # Fetch Higher Timeframes
                    df_1h = await asyncio.wait_for(market_data_service.fetch_ohlcv(symbol, '1h', 50), timeout=10.0)
                    df_4h = await asyncio.wait_for(market_data_service.fetch_ohlcv(symbol, '4h', 50), timeout=10.0)

                    if df_1h is None or df_4h is None:
                        logger.warning(f"MTF data missing for {symbol}. Skipping analysis.")
                        continue

                    # 4. SNIPER ANALYSIS
                    data_bundle = {"4h": df_4h, "1h": df_1h, "15m": df_15m}
                    signal = await signal_engine.analyze_sniper_setup(data_bundle, symbol)
                    
                    # Update Final Bias for UI
                    bias_text = "GOLDEN ZONE" if signal else "WAITING"
                    for i, item in enumerate(current_state):
                        if item["symbol"] == symbol:
                            current_state[i]["bias"] = bias_text
                            break
                    set_scanner_state(current_state)
                    await manager.broadcast({"type": "scanner_update", "data": current_state})

                    if signal:
                        logger.info(f"🎯 SNIPER SIGNAL: {symbol}")
                        stored = add_signal(signal)
                        await telegram_service.send_signal(stored)
                        await manager.broadcast({"type": "new_signal", "data": stored})

                except Exception as e:
                    logger.error(f"Error in {symbol} scan: {e}")
                    continue

        except Exception as e:
            logger.error(f"Global Scanner Loop Error: {e}")

        await asyncio.sleep(60) # Scan every minute

def start_scanner():
    asyncio.create_task(market_scanner())
