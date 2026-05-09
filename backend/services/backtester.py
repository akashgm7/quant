import pandas as pd
from services.market_data import market_data_service
from services.signal_engine import signal_engine
import asyncio
import logging

logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self):
        self.initial_balance = 10000.0
        self.fee_rate = 0.0004 # 0.04% fee

    async def run_backtest(self, symbol: str, timeframe: str, days: int = 30):
        """
        Runs a historical simulation of the strategy with expanded data limits.
        """
        # 1. Fetch Historical Data (Expanded to 5000 candles)
        # 15m: 4 per hour * 24 * days
        # 1h: 1 per hour * 24 * days
        needed = days * 24 * 4 if timeframe == "15m" else days * 24
        limit = min(needed, 5000)
        
        logger.info(f"Backtesting {symbol} | {timeframe} | {days} days | Limit: {limit}")
        df = await market_data_service.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        if df is None or len(df) < 50:
            return {"error": "Insufficient historical data fetched from exchange"}

        balance = self.initial_balance
        equity_curve = []
        trades = []
        
        # 2. Simulation Loop
        # Reduced indicator warmup to 30 candles to catch more early trades
        for i in range(30, len(df)):
            window = df.iloc[:i+1].copy()
            
            # Use the actual signal engine logic
            signal = await signal_engine.analyze_confluence(window, symbol, market_data_service)
            
            if signal:
                # Look ahead for result (Simulation)
                future_data = df.iloc[i+1:i+200] # Look ahead up to 200 candles (approx 2 days)
                
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
                    # Risk 2% per trade for the backtest
                    risk_amt = balance * 0.02
                    # 1:3 Risk Reward assumption if TP hit
                    pnl = risk_amt * 3.0 if outcome == "WIN" else -risk_amt
                    
                    # Deduct trading fees
                    pnl -= (balance * self.fee_rate * 2) # Entry + Exit
                    
                    balance += pnl
                    trades.append({
                        "timestamp": df.iloc[i]['timestamp'].isoformat(),
                        "direction": signal['direction'],
                        "entry": entry_price,
                        "outcome": outcome,
                        "pnl": round(pnl, 2),
                        "balance": round(balance, 2)
                    })
            
            # Downsample equity curve to avoid huge JSON response
            if i % 5 == 0:
                equity_curve.append({
                    "timestamp": df.iloc[i]['timestamp'].isoformat(),
                    "balance": round(balance, 2)
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
