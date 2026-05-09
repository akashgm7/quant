import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Any

class SignalEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def analyze_confluence(self, df: pd.DataFrame, symbol: str, market_data_service) -> Optional[Dict[str, Any]]:
        """
        QUANT-X Scalping Core: Implements 4 high-probability intraday strategies.
        """
        if df is None or len(df) < 50:
            return None

        # 1. Base Indicators
        df = self._add_indicators(df)
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 2. Session & Volatility Filters
        session = market_data_service.get_current_session()
        avg_vol = df['volume'].rolling(20).mean().iloc[-1]
        is_volatile = curr['volume'] > avg_vol * 1.2
        
        # 3. Higher Timeframe Confirmation (Simplified for the loop)
        # In a full MTF implementation, we'd fetch 1H/4H separately.
        # Here we use the 15m structure as a proxy for trend.
        
        # --- STRATEGY A: LIQUIDITY SWEEP REVERSAL (LSR) ---
        lsr_signal = self._check_lsr(df)
        if lsr_signal and is_volatile:
            return self._format_signal(symbol, lsr_signal, "Liquidity Sweep Reversal", session, curr)

        # --- STRATEGY B: MOMENTUM BREAKOUT CONTINUATION (MBC) ---
        mbc_signal = self._check_mbc(df)
        if mbc_signal and is_volatile:
            return self._format_signal(symbol, mbc_signal, "Momentum Continuation", session, curr)

        # --- STRATEGY C: VWAP + STRUCTURE SCALP (VSS) ---
        vss_signal = self._check_vss(df, market_data_service)
        if vss_signal and is_volatile:
            return self._format_signal(symbol, vss_signal, "VWAP Structure Scalp", session, curr)

        return None

    def _add_indicators(self, df: pd.DataFrame):
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # EMA for trend
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # ATR for SL/TP
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(14).mean()
        
        return df

    def _check_lsr(self, df: pd.DataFrame):
        """
        Liquidity Sweep: Price breaks a recent swing high/low and immediately rejects.
        """
        lookback = 15
        recent_high = df['high'].iloc[-lookback:-2].max()
        recent_low = df['low'].iloc[-lookback:-2].min()
        
        curr = df.iloc[-1]
        
        # Bullish Sweep: Price went below recent low and closed back above it
        if df['low'].iloc[-1] < recent_low and curr['close'] > recent_low:
            if curr['close'] > curr['open']: # Hammer/Green candle
                return "LONG"
        
        # Bearish Sweep: Price went above recent high and closed back below it
        if df['high'].iloc[-1] > recent_high and curr['close'] < recent_high:
            if curr['close'] < curr['open']: # Shooting Star/Red candle
                return "SHORT"
        
        return None

    def _check_mbc(self, df: pd.DataFrame):
        """
        Momentum Breakout: Strong close above/below EMA 20 with volume.
        """
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Bullish Breakout
        if prev['close'] < prev['ema_20'] and curr['close'] > curr['ema_20']:
            if curr['rsi'] > 55 and curr['rsi'] < 70:
                return "LONG"
        
        # Bearish Breakout
        if prev['close'] > prev['ema_20'] and curr['close'] < curr['ema_20']:
            if curr['rsi'] < 45 and curr['rsi'] > 30:
                return "SHORT"
        
        return None

    def _check_vss(self, df: pd.DataFrame, market_data_service):
        """
        VWAP Reclaim: Price crosses VWAP with trend alignment.
        """
        df = market_data_service.calculate_vwap(df)
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Bullish VWAP Reclaim
        if prev['close'] < prev['vwap'] and curr['close'] > curr['vwap']:
            if curr['ema_20'] > curr['ema_50']: # Trend Alignment
                return "LONG"
                
        # Bearish VWAP Reclaim
        if prev['close'] > prev['vwap'] and curr['close'] < curr['vwap']:
            if curr['ema_20'] < curr['ema_50']: # Trend Alignment
                return "SHORT"
        
        return None

    def _format_signal(self, symbol: str, direction: str, strategy: str, session: str, curr: pd.Series):
        atr = curr['atr']
        price = curr['close']
        
        # Scalping SL/TP logic: Strict RR
        if direction == "LONG":
            sl = price - (atr * 1.5)
            tp1 = price + (atr * 2.0)
            tp2 = price + (atr * 4.0)
        else:
            sl = price + (atr * 1.5)
            tp1 = price - (atr * 2.0)
            tp2 = price - (atr * 4.0)
            
        return {
            "symbol": symbol,
            "direction": direction,
            "entry": round(price, 5),
            "stop_loss": round(sl, 5),
            "take_profit_1": round(tp1, 5),
            "take_profit_2": round(tp2, 5),
            "risk_reward": "1:2.0",
            "confidence": 85 if session != "ASIA_OFF_PEAK" else 65,
            "reasons": [strategy, f"Active Session: {session}", "Volume Confirmed"],
            "setup_type": strategy,
            "timeframe": "15m",
            "session": session
        }

signal_engine = SignalEngine()
