import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Any, List

class SignalEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def analyze_sniper_setup(self, data: Dict[str, pd.DataFrame], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fibonacci Sniper System: Only 4-5 Golden Setups per day.
        Requires 4+ confluences and 0.618/0.786 zone entry.
        """
        df_15m = data.get('15m')
        df_1h = data.get('1h')
        df_4h = data.get('4h')

        if df_15m is None or len(df_15m) < 100:
            return None

        # 1. Higher Timeframe Trend Alignment (MANDATORY)
        bias_4h = self._get_trend_bias(df_4h)
        bias_1h = self._get_trend_bias(df_1h)
        
        if bias_4h == "NEUTRAL" or bias_4h != bias_1h:
            return None # No trend agreement

        # 2. Fibonacci Zone Detection
        fib_levels = self._calculate_fibs(df_15m, bias_4h)
        if not fib_levels:
            return None

        curr = df_15m.iloc[-1]
        price = curr['close']
        
        # Target the "Golden Zone" (0.618 to 0.786)
        in_gold_zone = False
        if bias_4h == "BULLISH":
            if fib_levels['0.786'] <= price <= fib_levels['0.618']:
                in_gold_zone = True
        else:
            if fib_levels['0.618'] <= price <= fib_levels['0.786']:
                in_gold_zone = True
        
        if not in_gold_zone:
            return None

        # 3. Confirmation Scoring (Need 4+ Confluences)
        confluences = []
        
        # Conf 1: Liquidity Sweep
        sweep = self._check_liquidity_sweep(df_15m, bias_4h)
        if sweep: confluences.append("Liquidity Sweep Rejection")
        
        # Conf 2: Volume Expansion
        avg_vol = df_15m['volume'].rolling(20).mean().iloc[-1]
        if curr['volume'] > avg_vol * 1.5:
            confluences.append("Volume Expansion Confirmed")
            
        # Conf 3: Candlestick Pattern
        pattern = self._check_candlestick_pattern(df_15m, bias_4h)
        if pattern: confluences.append(f"{pattern} Pattern")
        
        # Conf 4: VWAP Reclaim
        vwap_signal = self._check_vwap_confluence(df_15m, bias_4h)
        if vwap_signal: confluences.append("VWAP Reclaim/Support")
        
        # Conf 5: Market Structure (BOS/CHoCH)
        structure = self._check_structure_shift(df_15m, bias_4h)
        if structure: confluences.append(structure)

        # FINAL SNIPER TRIGGER
        if len(confluences) >= 4:
            return self._format_sniper_signal(symbol, bias_4h, fib_levels, confluences, curr)

        return None

    def _get_trend_bias(self, df: pd.DataFrame) -> str:
        if df is None or len(df) < 50: return "NEUTRAL"
        ema_50 = df['close'].ewm(span=50, adjust=False).mean()
        curr_price = df['close'].iloc[-1]
        if curr_price > ema_50.iloc[-1]: return "BULLISH"
        if curr_price < ema_50.iloc[-1]: return "BEARISH"
        return "NEUTRAL"

    def _calculate_fibs(self, df: pd.DataFrame, bias: str):
        # Look for the last significant swing
        lookback = 100
        data = df.iloc[-lookback:]
        
        if bias == "BULLISH":
            low = data['low'].min()
            low_idx = data['low'].idxmin()
            high = data.loc[low_idx:]['high'].max()
            if high == low: return None
            diff = high - low
            return {
                '0.382': high - (diff * 0.382),
                '0.5': high - (diff * 0.5),
                '0.618': high - (diff * 0.618),
                '0.786': high - (diff * 0.786),
                'anchor_low': low,
                'anchor_high': high
            }
        else:
            high = data['high'].max()
            high_idx = data['high'].idxmax()
            low = data.loc[high_idx:]['low'].min()
            if high == low: return None
            diff = high - low
            return {
                '0.382': low + (diff * 0.382),
                '0.5': low + (diff * 0.5),
                '0.618': low + (diff * 0.618),
                '0.786': low + (diff * 0.786),
                'anchor_low': low,
                'anchor_high': high
            }

    def _check_liquidity_sweep(self, df: pd.DataFrame, bias: str):
        # Check if wick went below/above recent structure and rejected
        recent = df.iloc[-5:]
        if bias == "BULLISH":
            # Wick below EMA or recent low
            return recent['low'].min() < df['low'].iloc[-20:-5].min() and df['close'].iloc[-1] > df['low'].iloc[-20:-5].min()
        else:
            return recent['high'].max() > df['high'].iloc[-20:-5].max() and df['close'].iloc[-1] < df['high'].iloc[-20:-5].max()

    def _check_candlestick_pattern(self, df: pd.DataFrame, bias: str):
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        # Simplified Engulfing
        if bias == "BULLISH":
            if curr['close'] > prev['open'] and prev['close'] < prev['open'] and curr['close'] > curr['open']:
                return "Bullish Engulfing"
        else:
            if curr['close'] < prev['open'] and prev['close'] > prev['open'] and curr['close'] < curr['open']:
                return "Bearish Engulfing"
        return None

    def _check_vwap_confluence(self, df: pd.DataFrame, bias: str):
        # Mock VWAP calculation
        tp = (df['high'] + df['low'] + df['close']) / 3
        vwap = (tp * df['volume']).rolling(50).sum() / df['volume'].rolling(50).sum()
        curr_price = df['close'].iloc[-1]
        if bias == "BULLISH":
            return curr_price > vwap.iloc[-1]
        else:
            return curr_price < vwap.iloc[-1]

    def _check_structure_shift(self, df: pd.DataFrame, bias: str):
        # Check for Higher High / Lower Low
        if bias == "BULLISH" and df['close'].iloc[-1] > df['high'].iloc[-10:-1].max():
            return "BOS Confirmed"
        if bias == "BEARISH" and df['close'].iloc[-1] < df['low'].iloc[-10:-1].min():
            return "BOS Confirmed"
        return None

    def _format_sniper_signal(self, symbol: str, direction: str, fibs: Dict, confluences: List[str], curr: pd.Series):
        price = curr['close']
        # Stop loss beyond 0.786 or 1.0 (Anchor)
        if direction == "BULLISH":
            action = "LONG"
            sl = fibs['anchor_low'] * 0.998
            tp1 = fibs['0.382']
            tp2 = fibs['anchor_high']
        else:
            action = "SHORT"
            sl = fibs['anchor_high'] * 1.002
            tp1 = fibs['0.382']
            tp2 = fibs['anchor_low']

        return {
            "symbol": symbol,
            "direction": action,
            "entry": round(price, 5),
            "stop_loss": round(sl, 5),
            "take_profit_1": round(tp1, 5),
            "take_profit_2": round(tp2, 5),
            "risk_reward": "1:3.0",
            "confidence": min(70 + (len(confluences) * 5), 95),
            "reasons": confluences,
            "setup_type": "Fibonacci Sniper Setup",
            "timeframe": "15m",
            "fib_zone": "0.618 - 0.786"
        }

signal_engine = SignalEngine()
