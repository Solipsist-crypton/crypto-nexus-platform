from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class VirtualTrade(Base):
    """Модель для віртуальних тестових угод"""
    __tablename__ = "virtual_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Якщо буде авторизація
    signal_id = Column(Integer, ForeignKey("futures_signals.id"))
    
    # Цінові рівні
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    take_profit = Column(Float)
    stop_loss = Column(Float)
    
    # Статус та результати
    status = Column(String, default="active")  # active, tp_hit, sl_hit, cancelled, expired
    pnl_percentage = Column(Float, default=0.0)
    pnl_amount = Column(Float, default=0.0)
    
    # Час
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    # Зв'язки
    signal = relationship("Signal")
    
    def __repr__(self):
        return f"<VirtualTrade {self.id}: {self.status} PnL: {self.pnl_percentage:.2f}%>"
    
    def calculate_pnl(self, current_price: float = None) -> float:
        """
        Розрахунок PnL на основі поточної ціни
        
        Args:
            current_price: Поточна ціна (якщо None - використовуємо збережену)
            
        Returns:
            PnL у відсотках
        """
        if current_price is not None:
            self.current_price = current_price
        
        if not self.current_price:
            return 0.0
        
        # Для long: (current - entry) / entry
        # Для short: (entry - current) / entry
        price_diff = self.current_price - self.entry_price
        self.pnl_percentage = (price_diff / self.entry_price) * 100
        
        # Припустимий розмір позиції (тимчасово фіксований)
        position_size = 1000  # $1000 для тесту
        self.pnl_amount = position_size * (self.pnl_percentage / 100)
        
        # Перевіряємо TP/SL
        if self.pnl_percentage >= ((self.take_profit - self.entry_price) / self.entry_price * 100):
            self.status = "tp_hit"
        elif self.pnl_percentage <= ((self.stop_loss - self.entry_price) / self.entry_price * 100):
            self.status = "sl_hit"
        
        return self.pnl_percentage
    
    def to_dict(self):
        """Серіалізація для API"""
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "user_id": self.user_id,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "status": self.status,
            "pnl_percentage": round(self.pnl_percentage, 2),
            "pnl_amount": round(self.pnl_amount, 2),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }