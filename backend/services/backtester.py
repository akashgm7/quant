import pandas as pd
from services.market_data import market_data_service
from services.signal_engine import signal_engine
import asyncio

class Backtester:
    def __init__(self):
        self.initial_balance = 10000.0
        self.fee_rate = 0.0004 # 0.04% Binance Futures fee

    async def run_backtest(self, symbol: str, timeframe: str, days: int = 30):
        """
        Runs a historical simulation of the strategy.
        """
        # 1. Fetch Historical Data (approx 1000 candles)
        limit = days * 24 * 4 if timeframe == "15m" else days * 24
        df = await market_data_service.fetch_ohlcv(symbol, timeframe, limit=min(limit, 1000))
        
        if df is None or len(df) < 100:
            return {"error": "Insufficient historical data"}

        balance = self.initial_balance
        equity_curve = []
        trades = []
        
        # 2. Simulation Loop (Walk-forward)
        # We start from index 50 to have enough data for indicators
        for i in range(50, len(df)):
            window = df.iloc[:i+1].copy()
            signal = await signal_engine.analyze_confluence(window, symbol, market_data_service)
            
            if signal:
                # Check outcome (Simulated SL/TP hit)
                # For simplicity in this backtest, we check the future price action
                future_data = df.iloc[i+1:i+100] # Look ahead up to 100 candles
                
                entry_price = signal['entry']
                sl = signal['stop_loss']
                tp = signal['take_profit_1']
                
                outcome = None
                for _, candle in future_data.iterrows():
                    if signal['direction'] == "LONG":
                        if candle['low'] <= sl:
                            outcome = "LOSS"
                            break
                        if candle['high'] >= tp:
                            outcome = "WIN"
                            break
                    else:
                        if candle['high'] >= sl:
                            outcome = "LOSS"
                            break
                        if candle['low'] <= tp:
                            outcome = "WIN"
                            break
                
                if outcome:
                    # Calculate PnL (Risk 1% of balance)
                    risk_amt = balance * 0.01
                    pnl = risk_amt * 2.0 if outcome == "WIN" else -risk_amt
                    
                    # Deduct fees
                    pnl -= (balance * self.fee_rate)
                    
                    balance += pnl
                    trades.append({
                        "timestamp": df.iloc[i]['timestamp'],
                        "direction": signal['direction'],
                        "entry": entry_price,
                        "outcome": outcome,
                        "pnl": pnl,
                        "balance": balance
                    })
            
            equity_curve.append({
                "timestamp": df.iloc[i]['timestamp'],
                "balance": balance
            })

        # 3. Calculate Stats
        wins = len([t for t in trades if t['outcome'] == "WIN"])
        total = len(trades)
        win_rate = (wins / total * 100) if total > 0 else 0
        
        return {
            "symbol": symbol,
            "total_trades": total,
            "win_rate": round(win_rate, 2),
            "final_balance": round(balance, 2),
            "net_profit": round(balance - self.initial_balance, 2),
            "trades": trades,
            "equity_curve": equity_curve
        }

backtester = Backtester()
