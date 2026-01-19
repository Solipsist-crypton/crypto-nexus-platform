from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)
    timeframe = Column(String(10), default="4H")
    
    entry_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    
    confidence_score = Column(Float, nullable=False, default=0.0)
    reasoning_weights = Column(JSON, nullable=True)
    explanation_text = Column(Text, nullable=True)
    
    status = Column(String(20), default="ACTIVE")
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Signal {self.symbol} {self.direction} ({self.confidence_score:.2f})>"

class VirtualTrade(Base):
    __tablename__ = "virtual_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"))
    
    entry_price = Column(Float, nullable=False)
    position_size = Column(Float, default=100.0)
    take_profit_price = Column(Float, nullable=False)
    stop_loss_price = Column(Float, nullable=False)
    
    status = Column(String(20), default="ACTIVE")
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)
    
    pnl_percent = Column(Float, nullable=True)
    pnl_usdt = Column(Float, nullable=True)