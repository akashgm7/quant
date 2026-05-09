import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import logging

class MarketDataService:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        self.logger = logging.getLogger(__name__)

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return None

    async def get_market_structure(self, df: pd.DataFrame):
        """
        Sophisticated logic to detect BOS (Break of Structure) and CHoCH (Change of Character).
        """
        if df is None or len(df) < 50:
            return {"bias": "UNKNOWN", "bos": False, "choch": False}
        
        # Calculate swings
        df['swing_high'] = df['high'][(df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))]
        df['swing_low'] = df['low'][(df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))]
        
        last_high = df['swing_high'].dropna().iloc[-1]
        last_low = df['swing_low'].dropna().iloc[-1]
        prev_high = df['swing_high'].dropna().iloc[-2]
        prev_low = df['swing_low'].dropna().iloc[-2]
        
        current_close = df['close'].iloc[-1]
        
        bos = False
        choch = False
        bias = "NEUTRAL"
        
        # Bullish BOS: Breaking above previous swing high
        if current_close > last_high:
            bos = True
            bias = "BULLISH"
            
        # Bearish BOS: Breaking below previous swing low
        if current_close < last_low:
            bos = True
            bias = "BEARISH"
            
        # CHoCH: Change of Character (Simplified)
        if bias == "BULLISH" and current_close < last_low:
            choch = True
            bias = "BEARISH"
        elif bias == "BEARISH" and current_close > last_high:
            choch = True
            bias = "BULLISH"
            
        return {
            "bias": bias,
            "bos": bos,
            "choch": choch,
            "last_high": last_high,
            "last_low": last_low
        }

    async def close(self):
        await self.exchange.close()

market_data_service = MarketDataService()
