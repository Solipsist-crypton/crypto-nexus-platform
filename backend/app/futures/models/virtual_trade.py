# backend/app/futures/models/virtual_trade.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class VirtualTrade(Base):
    __tablename__ = "virtual_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ForeignKey до сигналу (важливо!)
    signal_id = Column(Integer, ForeignKey("futures_signals.id"), nullable=False)
    
    # Для user_id (тимчасово, поки немає users таблиці)
    user_id = Column(Integer, default=1)
    
    # Торгові параметри
    symbol = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # long/short
    entry_price = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    
    # Статус та PnL
    status = Column(String, default="active")  # active/tp_hit/sl_hit/closed
    pnl_percentage = Column(Float, default=0.0)
    pnl_amount = Column(Float, default=0.0)
    
    # Таймстампи
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Відносини
    signal = relationship("Signal", back_populates="virtual_trades")
    
    def calculate_pnl(self, current_price: float):
        """Розрахунок PnL на основі поточної ціни"""
        self.current_price = current_price
        
        if self.direction == "long":
            self.pnl_percentage = ((current_price - self.entry_price) / self.entry_price) * 100
        else:  # short
            self.pnl_percentage = ((self.entry_price - current_price) / self.entry_price) * 100
        
        # Перевірка TP/SL
        if self.direction == "long":
            if current_price >= self.take_profit:
                self.status = "tp_hit"
            elif current_price <= self.stop_loss:
                self.status = "sl_hit"
        else:  # short
            if current_price <= self.take_profit:
                self.status = "tp_hit"
            elif current_price >= self.stop_loss:
                self.status = "sl_hit"
        
        return self.pnl_percentage
    
    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "status": self.status,
            "pnl_percentage": round(self.pnl_percentage, 2),
            "pnl_amount": round(self.pnl_amount, 2),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "signal_id": self.signal_id
        }