from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TradeSignal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    direction = Column(String)  # LONG/SHORT
    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profit_1 = Column(Float)
    take_profit_2 = Column(Float)
    confidence_score = Column(Integer)
    reasoning = Column(JSON)
    status = Column(String, default="PENDING")  # PENDING, COMPLETED, FAILED
    outcome = Column(String, nullable=True)  # WIN, LOSS
    journal_notes = Column(String, nullable=True)
    ml_features = Column(JSON, nullable=True) # Raw indicators for ML training
    created_at = Column(DateTime, default=datetime.utcnow)
    
class MarketStat(Base):
    __tablename__ = "market_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    win_rate = Column(Float)
    total_trades = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)
