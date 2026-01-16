from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from ..database import Base
from datetime import datetime

class ExchangeMetrics(Base):
    __tablename__ = "exchange_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, index=True)  # Binance, Kraken, Bybit
    coin = Column(String, index=True)      # BTC, ETH, SOL
    pair = Column(String)                  # BTCUSDT, XXBTZUSD
    
    # Комісії
    maker_fee = Column(Float)              # 0.001 = 0.1%
    taker_fee = Column(Float)              # 0.001 = 0.1%
    withdrawal_fee = Column(Float)         # Комісія на вивід
    min_withdrawal = Column(Float)         # Мінімальний вивід
    
    # Ліквідність
    daily_volume = Column(Float)           # Денний обсяг
    spread = Column(Float)                 # Спред bid/ask
    liquidity_score = Column(Float)        # 0-1 оцінка ліквідності
    
    # Прапорці
    is_active = Column(Boolean, default=True)
    supports_deposit = Column(Boolean, default=True)
    supports_withdrawal = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExchangeMetrics {self.exchange}-{self.coin} maker:{self.maker_fee}%>"