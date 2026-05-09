import pandas as pd
import numpy as np
import logging

def calc_rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(length).mean()
    loss = (-delta.clip(upper=0)).rolling(length).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    high, low, close = df['high'], df['low'], df['close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(length).mean()

def calc_ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()

class SignalEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def analyze_confluence(self, df: pd.DataFrame, symbol: str, market_data_service):
        """
        Analyzes the dataframe for institutional setups.
        """
        if df is None or len(df) < 50:
            return None

        # Technical Indicators (native pandas)
        df['RSI_14']   = calc_rsi(df['close'], 14)
        df['ATRr_14']  = calc_atr(df, 14)
        df['EMA_20']   = calc_ema(df['close'], 20)
        df['EMA_50']   = calc_ema(df['close'], 50)
        df['EMA_200']  = calc_ema(df['close'], 200)

        # 1. Market Structure Alignment
        structure = await market_data_service.get_market_structure(df)
        htf_bias = structure["bias"]
        
        current_candle = df.iloc[-1]
        
        # 2. Liquidity Sweep Detection (Simplified)
        # Check for a "sweep" of recent lows/highs followed by a reversal
        recent_low = df['low'].iloc[-20:-2].min()
        recent_high = df['high'].iloc[-20:-2].max()
        
        is_bullish_sweep = current_candle['low'] < recent_low and current_candle['close'] > recent_low
        is_bearish_sweep = current_candle['high'] > recent_high and current_candle['close'] < recent_high

        # 3. Volume Confirmation
        avg_volume = df['volume'].iloc[-20:].mean()
        high_volume = current_candle['volume'] > (avg_volume * 1.5)

        # 4. Momentum Filter
        bullish_momentum = current_candle['RSI_14'] > 50 and current_candle['RSI_14'] < 70
        bearish_momentum = current_candle['RSI_14'] < 50 and current_candle['RSI_14'] > 30

        # Signal Logic
        signal = None
        confidence = 0
        reasons = []

        if htf_bias == "BULLISH" and is_bullish_sweep:
            confidence += 40
            reasons.append("HTF Bullish Alignment")
            reasons.append("Bullish Liquidity Sweep")
            
            if high_volume:
                confidence += 20
                reasons.append("High Volume Confirmation")
            if bullish_momentum:
                confidence += 20
                reasons.append("Positive Momentum")
            
            if confidence >= 60:
                signal = "LONG"

        elif htf_bias == "BEARISH" and is_bearish_sweep:
            confidence += 40
            reasons.append("HTF Bearish Alignment")
            reasons.append("Bearish Liquidity Sweep")
            
            if high_volume:
                confidence += 20
                reasons.append("High Volume Confirmation")
            if bearish_momentum:
                confidence += 20
                reasons.append("Negative Momentum")
            
            if confidence >= 60:
                signal = "SHORT"

        if signal:
            # Risk Management Calculation
            atr = current_candle['ATRr_14']
            entry = current_candle['close']
            
            if signal == "LONG":
                sl = entry - (atr * 2)
                tp1 = entry + (atr * 2)
                tp2 = entry + (atr * 4)
            else:
                sl = entry + (atr * 2)
                tp1 = entry - (atr * 2)
                tp2 = entry - (atr * 4)
            
            # Extract ML Features
            ml_features = {
                "rsi": current_candle['RSI_14'],
                "atr": current_candle['ATRr_14'],
                "ema_20_50_diff": current_candle['EMA_20'] - current_candle['EMA_50'],
                "vol_relative": current_candle['volume'] / avg_volume if avg_volume > 0 else 1.0,
                "htf_bias": htf_bias,
                "is_sweep": True # Since we are in the signal block
            }

            return {
                "symbol": symbol,
                "direction": signal,
                "entry": entry,
                "stop_loss": sl,
                "take_profit_1": tp1,
                "take_profit_2": tp2,
                "confidence": confidence,
                "reasons": reasons,
                "risk_reward": 2.0,
                "ml_features": ml_features
            }

        return None

signal_engine = SignalEngine()
