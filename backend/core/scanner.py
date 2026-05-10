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
    
    # Initialize state
    initial_state = [{"symbol": p, "bias": "ANALYZING", "volatility": "-", "rsi": 0, "price": 0} for p in PAIRS]
    set_scanner_state(initial_state)

    while True:
        try:
            current_state = get_scanner_state()
            
            for symbol in PAIRS:
                # 1. Check Cooldown (SNIPER RULE)
                if is_in_cooldown(symbol):
                    logger.info(f"⏭️ {symbol} in cooldown. Skipping.")
                    continue

                # 2. Fetch Multi-TF Data (4H, 1H, 15m)
                try:
                    df_4h, df_1h, df_15m = await market_data_service.get_multi_tf_data(symbol)
                    
                    if df_15m is None or df_1h is None or df_4h is None:
                        continue

                    # Update Dashboard State
                    for i, item in enumerate(current_state):
                        if item["symbol"] == symbol:
                            current_state[i].update({
                                "price": float(df_15m['close'].iloc[-1]),
                                "bias": "SEARCHING FOR GOLDEN ZONE"
                            })
                            break
                    
                    set_scanner_state(current_state)
                    await manager.broadcast({"type": "scanner_update", "data": current_state})

                    # 3. SNIPER ANALYSIS
                    data_bundle = {"4h": df_4h, "1h": df_1h, "15m": df_15m}
                    signal = await signal_engine.analyze_sniper_setup(data_bundle, symbol)
                    
                    if signal:
                        logger.info(f"🎯 GOLDEN SETUP DETECTED: {symbol} {signal['direction']}")
                        stored = add_signal(signal)
                        await telegram_service.send_signal(stored)
                        await manager.broadcast({"type": "new_signal", "data": stored})

                except Exception as e:
                    logger.error(f"Error scanning {symbol}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Scanner loop error: {e}")

        # Sniper mode is patient. 2-minute refresh is plenty.
        await asyncio.sleep(120)

def start_scanner():
    asyncio.create_task(market_scanner())
