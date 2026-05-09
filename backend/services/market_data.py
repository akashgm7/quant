import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import logging
import random
from datetime import datetime, time

class MarketDataService:
    def __init__(self):
        self.exchanges = {
            'bybit': ccxt.bybit({'enableRateLimit': True, 'options': {'defaultType': 'linear'}}),
            'mexc': ccxt.mexc({'enableRateLimit': True}),
            'gateio': ccxt.gateio({'enableRateLimit': True})
        }
        self.logger = logging.getLogger(__name__)

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 100):
        for name, exchange in self.exchanges.items():
            try:
                ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                if ohlcv and len(ohlcv) > 0:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    return df
            except Exception:
                continue
        return None

    def get_current_session(self):
        """
        Detects active trading session (UTC).
        London: 08:00 - 16:00
        NY: 13:00 - 21:00
        Overlap: 13:00 - 16:00
        """
        now_utc = datetime.utcnow().time()
        
        is_london = time(8, 0) <= now_utc <= time(16, 0)
        is_ny = time(13, 0) <= now_utc <= time(21, 0)
        
        if is_london and is_ny: return "LONDON_NY_OVERLAP"
        if is_london: return "LONDON"
        if is_ny: return "NEW_YORK"
        return "ASIA_OFF_PEAK"

    async def get_multi_tf_data(self, symbol: str):
        """
        Fetches 4H, 1H, and 15m data for a pair to confirm bias.
        """
        tasks = [
            self.fetch_ohlcv(symbol, '4h', 50),
            self.fetch_ohlcv(symbol, '1h', 50),
            self.fetch_ohlcv(symbol, '15m', 100)
        ]
        return await asyncio.gather(*tasks)

    def calculate_vwap(self, df: pd.DataFrame):
        """
        Calculates Volume Weighted Average Price (Intraday).
        """
        df['tp'] = (df['high'] + df['low'] + df['close']) / 3
        df['tp_vol'] = df['tp'] * df['volume']
        # For scalping, we often use a rolling VWAP or session-reset VWAP
        # Here we use a rolling 100-period as a proxy for intraday VWAP
        df['vwap'] = df['tp_vol'].rolling(window=100).sum() / df['volume'].rolling(window=100).sum()
        return df

    async def close(self):
        for exchange in self.exchanges.values():
            await exchange.close()

market_data_service = MarketDataService()
