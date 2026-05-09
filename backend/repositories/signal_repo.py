from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.trade import TradeSignal
from datetime import datetime

class SignalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_signal(self, signal_data: dict):
        db_signal = TradeSignal(
            symbol=signal_data["symbol"],
            direction=signal_data["direction"],
            entry_price=signal_data["entry"],
            stop_loss=signal_data["stop_loss"],
            take_profit_1=signal_data["take_profit_1"],
            take_profit_2=signal_data["take_profit_2"],
            confidence_score=signal_data["confidence"],
            reasoning=signal_data["reasons"],
            ml_features=signal_data.get("ml_features"),
            created_at=datetime.utcnow()
        )
        self.db.add(db_signal)
        await self.db.commit()
        await self.db.refresh(db_signal)
        return db_signal

    async def get_active_signals(self, limit: int = 20):
        result = await self.db.execute(
            select(TradeSignal).order_by(TradeSignal.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def update_signal(self, signal_id: int, update_data: dict):
        result = await self.db.execute(select(TradeSignal).filter(TradeSignal.id == signal_id))
        db_signal = result.scalar_one_or_none()
        if db_signal:
            for key, value in update_data.items():
                setattr(db_signal, key, value)
            await self.db.commit()
            await self.db.refresh(db_signal)
        return db_signal
