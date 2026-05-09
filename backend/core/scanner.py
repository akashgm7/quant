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
    
    # Initial Loading State
    initial_state = [{"symbol": p, "bias": "FETCHING", "volatility": "-", "rsi": 0, "price": 0} for p in PAIRS]
    set_scanner_state(initial_state)

    while True:
        try:
            current_state = get_scanner_state()
            
            for symbol in PAIRS:
                # 1. Quick Price Fetch (Fallback)
                try:
                    # Try to get just the ticker first so the UI isn't empty
                    ticker = await asyncio.wait_for(market_data_service.exchanges['mexc'].fetch_ticker(symbol), timeout=5.0)
                    if ticker:
                        for i, item in enumerate(current_state):
                            if item["symbol"] == symbol:
                                current_state[i]["price"] = float(ticker['last'])
                                current_state[i]["bias"] = "SCANNING..."
                                break
                        set_scanner_state(current_state)
                        await manager.broadcast({"type": "scanner_update", "data": current_state})
                except Exception:
                    pass

                for tf in TIMEFRAMES:
                    try:
                        logger.info(f"Scanning {symbol} ({tf})...")
                        # Add a 10-second timeout to prevent hanging the whole loop
                        df = await asyncio.wait_for(market_data_service.fetch_ohlcv(symbol, timeframe=tf, limit=100), timeout=10.0)
                        
                        if df is None:
                            continue

                        if tf == "15m":
                            structure = await market_data_service.get_market_structure(df)
                            avg_vol = df['volume'].iloc[-20:].mean()
                            curr_vol = df['volume'].iloc[-1]
                            
                            for i, item in enumerate(current_state):
                                if item["symbol"] == symbol:
                                    current_state[i].update({
                                        "bias": structure["bias"],
                                        "volatility": "High" if curr_vol > avg_vol * 1.5 else "Normal",
                                        "price": float(df['close'].iloc[-1]),
                                        "rsi": 50.0
                                    })
                                    break
                            
                            set_scanner_state(current_state)
                            await manager.broadcast({"type": "scanner_update", "data": current_state})

                        # SIGNAL ANALYSIS
                        signal = await signal_engine.analyze_confluence(df, symbol, market_data_service)
                        if signal:
                            signal["timeframe"] = tf
                            stored = add_signal(signal)
                            await telegram_service.send_signal(stored)
                            await manager.broadcast({"type": "new_signal", "data": stored})
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout scanning {symbol} {tf}")
                        continue
                    except Exception as e:
                        logger.error(f"Error scanning {symbol} {tf}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Scanner loop error: {e}")

        await asyncio.sleep(20)

def start_scanner():
    asyncio.create_task(market_scanner())
