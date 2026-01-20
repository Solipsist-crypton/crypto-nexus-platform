from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, Text
from sqlalchemy.sql import func
from backend.app.database import Base

class Signal(Base):
    __tablename__ = "futures_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основні поля сигналу
    symbol = Column(String, nullable=False)  # Напр: BTCUSDT
    direction = Column(String, nullable=False)  # long/short
    timeframe = Column(String)  # Напр: 1h, 4h, 1d
    
    # Цінові рівні
    entry_price = Column(Float)
    take_profit = Column(Float)
    stop_loss = Column(Float)
    
    # AI логіка та пояснення
    confidence_score = Column(Float)  # 0.0 - 1.0
    reasoning_weights = Column(JSON)  # JSON з вагами факторів
    explanation_text = Column(Text)   # Текстове пояснення
    
    # Метадані
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Signal {self.symbol} {self.direction} {self.timeframe}>"