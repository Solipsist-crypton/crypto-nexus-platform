from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .base import FuturesBase  # Імпортуємо окремий Base!

class Signal(FuturesBase):
    """Модель для AI-сигналів"""
    __tablename__ = "futures_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)  # BTCUSDT, ETHUSDT
    direction = Column(String, nullable=False)  # long/short
    timeframe = Column(String, default="1h")  # 1h, 4h, 1d
    
    # Цінові рівні
    entry_price = Column(Float)
    take_profit = Column(Float)
    stop_loss = Column(Float)
    
    # AI-аналіз
    confidence = Column(Float, default=0.0)  # 0.0-1.0
    reasoning = Column(JSON)  # JSON з вагами факторів
    explanation = Column(Text)  # Текстове пояснення
    
    # Метадані
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    source = Column(String, default="ai_v1")  # ai_v1, manual, etc
    
    def __repr__(self):
        return f"<FutureSignal {self.symbol} {self.direction} ({self.confidence:.2f})>"
    
    def to_dict(self):
        """Серіалізація для API"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "direction": self.direction,
            "timeframe": self.timeframe,
            "entry_price": self.entry_price,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }