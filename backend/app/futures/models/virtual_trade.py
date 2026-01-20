from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class VirtualTrade(Base):
    __tablename__ = "virtual_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    signal_id = Column(Integer, ForeignKey("futures_signals.id"))
    
    # Цінові рівні
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    take_profit = Column(Float)
    stop_loss = Column(Float)
    
    # Статус та результати
    status = Column(String, default="active")  # active, tp_hit, sl_hit, cancelled
    pnl_percentage = Column(Float, default=0.0)
    pnl_amount = Column(Float, default=0.0)
    
    # Час
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    # Зв'язки
    signal = relationship("Signal")
    
    def calculate_pnl(self):
        """Розрахунок PnL на основі поточної ціни"""
        if not self.current_price:
            return 0.0
        
        price_diff = self.current_price - self.entry_price
        self.pnl_percentage = (price_diff / self.entry_price) * 100
        return self.pnl_percentage