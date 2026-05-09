import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import logging
import random

class MarketDataService:
    def __init__(self):
        # We'll try multiple exchanges if one fails due to IP blocks
        self.exchanges = {
            'bybit': ccxt.bybit({'enableRateLimit': True, 'options': {'defaultType': 'linear'}}),
            'mexc': ccxt.mexc({'enableRateLimit': True}),
            'gateio': ccxt.gateio({'enableRateLimit': True})
        }
        self.logger = logging.getLogger(__name__)

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 100):
        # Try each exchange until one works
        for name, exchange in self.exchanges.items():
            try:
                self.logger.info(f"Attempting to fetch {symbol} from {name}...")
                ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                if ohlcv and len(ohlcv) > 0:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    self.logger.info(f"✅ Successfully fetched {symbol} from {name}")
                    return df
            except Exception as e:
                self.logger.warning(f"⚠️ {name} failed for {symbol}: {str(e)[:100]}")
                continue
        
        self.logger.error(f"❌ All exchanges failed for {symbol}")
        return None

    async def get_market_structure(self, df: pd.DataFrame):
        if df is None or len(df) < 20:
            return {"bias": "NEUTRAL", "bos": False, "choch": False, "last_high": 0, "last_low": 0}
        
        try:
            highs = df['high'].iloc[-20:]
            lows = df['low'].iloc[-20:]
            last_high = float(highs.max())
            last_low = float(lows.min())
            current_close = float(df['close'].iloc[-1])

            bias = "NEUTRAL"
            if current_close > (last_high + last_low) / 2:
                bias = "BULLISH"
            elif current_close < (last_high + last_low) / 2:
                bias = "BEARISH"

            return {
                "bias": bias,
                "bos": current_close > last_high * 0.99,
                "choch": False,
                "last_high": last_high,
                "last_low": last_low
            }
        except Exception as e:
            return {"bias": "NEUTRAL", "bos": False, "choch": False, "last_high": 0, "last_low": 0}

    async def close(self):
        for exchange in self.exchanges.values():
            await exchange.close()

market_data_service = MarketDataService()
