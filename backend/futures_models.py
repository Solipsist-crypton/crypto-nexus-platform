from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.futures_database import FuturesBase  # Імпортуємо свій окремий Base

class Signal(FuturesBase):
    """Модель AI-сигналу для ф’ючерсів"""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)  # BTCUSDT, ETHUSDT
    direction = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    timeframe = Column(String(10), default="4H")    # 15M, 1H, 4H, 1D

    # Цінові рівні
    entry_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)

    # AI-логіка
    confidence_score = Column(Float, nullable=False, default=0.0)  # 0.0-1.0
    reasoning_weights = Column(JSON, nullable=True)   # {"rsi": 0.8, "volume": 0.6}
    explanation_text = Column(Text, nullable=True)

    # Статус
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, TRIGGERED, EXPIRED
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)

    # Зв'язок з віртуальними угодами
    virtual_trades = relationship("VirtualTrade", back_populates="signal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Signal {self.symbol} {self.direction} (conf: {self.confidence_score:.2f})>"

    def calculate_expiry(self):
        """Обчислює expires_at на основі timeframe"""
        if self.timeframe == "15M":
            self.expires_at = self.generated_at + timedelta(minutes=15)
        elif self.timeframe == "1H":
            self.expires_at = self.generated_at + timedelta(hours=1)
        elif self.timeframe == "4H":
            self.expires_at = self.generated_at + timedelta(hours=4)
        elif self.timeframe == "1D":
            self.expires_at = self.generated_at + timedelta(days=1)
        else:
            self.expires_at = self.generated_at + timedelta(hours=4)  # default 4H


class VirtualTrade(FuturesBase):
    """Віртуальна угода для тестування сигналу"""
    __tablename__ = "virtual_trades"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False, index=True)

    # Параметри угоди
    entry_price = Column(Float, nullable=False)
    position_size = Column(Float, default=100.0)  # Умовна сума в USDT
    take_profit_price = Column(Float, nullable=False)
    stop_loss_price = Column(Float, nullable=False)

    # Статус
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, TP_HIT, SL_HIT, CANCELLED
    entry_time = Column(DateTime, default=datetime.utcnow, index=True)
    exit_time = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)

    # Результат
    pnl_percent = Column(Float, nullable=True)  # +2.5 або -1.8
    pnl_usdt = Column(Float, nullable=True)     # Результат у $

    # Зв'язок з сигналом
    signal = relationship("Signal", back_populates="virtual_trades")

    def calculate_pnl(self, current_price: float = None):
        """Розрахунок PnL. Якщо передана current_price, розраховує поточний, інакше - фінальний."""
        price = current_price if current_price is not None else self.exit_price
        if price is None or self.entry_price is None:
            return None

        price_diff = price - self.entry_price
        self.pnl_percent = (price_diff / self.entry_price) * 100
        self.pnl_usdt = (self.position_size * self.pnl_percent) / 100
        return self.pnl_percent