import asyncio
import logging
from services.market_data import market_data_service
from services.signal_engine import signal_engine
from services.telegram_bot import telegram_service
from core.websocket_manager import manager
from core.store import add_signal, set_scanner_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]

async def market_scanner():
    logger.info("Market Scanner started.")
    while True:
        try:
            scanner_snapshot = []

            for symbol in PAIRS:
                logger.info(f"Scanning {symbol}...")
                df = await market_data_service.fetch_ohlcv(symbol, timeframe="15m", limit=100)
                if df is None:
                    continue

                # Build scanner state for this pair
                structure = await market_data_service.get_market_structure(df)
                avg_vol = df['volume'].iloc[-20:].mean()
                curr_vol = df['volume'].iloc[-1]
                vol_status = "High" if curr_vol > avg_vol * 1.5 else "Normal"

                # RSI
                delta = df['close'].diff()
                gain = delta.clip(lower=0).rolling(14).mean()
                loss = (-delta.clip(upper=0)).rolling(14).mean()
                rs = gain / loss
                rsi = float((100 - (100 / (1 + rs))).iloc[-1])
                if rsi != rsi:  # nan check
                    rsi = 50.0

                scanner_snapshot.append({
                    "symbol": symbol,
                    "bias": structure["bias"],
                    "volatility": vol_status,
                    "rsi": round(rsi, 2),
                    "price": float(df['close'].iloc[-1]),
                    "change_24h": 0.0
                })

                # Signal Analysis
                signal = await signal_engine.analyze_confluence(df, symbol, market_data_service)
                if signal:
                    logger.info(f"🚨 Signal: {symbol} {signal['direction']} @ {signal['entry']:.2f}")
                    stored = add_signal(signal)

                    # Telegram Alert
                    try:
                        await telegram_service.send_signal(signal)
                    except Exception as e:
                        logger.warning(f"Telegram error: {e}")

                    # WebSocket Broadcast
                    try:
                        await manager.broadcast({
                            "type": "new_signal",
                            "data": stored
                        })
                    except Exception as e:
                        logger.warning(f"WebSocket broadcast error: {e}")

            # Update scanner state and broadcast
            set_scanner_state(scanner_snapshot)
            try:
                await manager.broadcast({
                    "type": "scanner_update",
                    "data": scanner_snapshot
                })
            except Exception as e:
                logger.warning(f"Scanner broadcast error: {e}")

        except Exception as e:
            logger.error(f"Scanner loop error: {e}", exc_info=True)

        await asyncio.sleep(60)  # Scan every 60 seconds


def start_scanner():
    asyncio.create_task(market_scanner())
