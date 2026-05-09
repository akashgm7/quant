import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import logging
import random

class MarketDataService:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            },
            'headers': {
                'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 120)}.0.0.0 Safari/537.36'
            }
        })
        self.logger = logging.getLogger(__name__)

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                self.logger.warning(f"Empty OHLCV returned for {symbol}")
                return None
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            self.logger.error(f"❌ CCXT Error ({symbol}): {e}")
            return None

    async def get_market_structure(self, df: pd.DataFrame):
        if df is None or len(df) < 20:
            return {"bias": "NEUTRAL", "bos": False, "choch": False, "last_high": 0, "last_low": 0}
        
        try:
            # Simple structure detection for the scanner
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
            self.logger.error(f"Error in market structure calc: {e}")
            return {"bias": "NEUTRAL", "bos": False, "choch": False, "last_high": 0, "last_low": 0}

    async def close(self):
        await self.exchange.close()

market_data_service = MarketDataService()
