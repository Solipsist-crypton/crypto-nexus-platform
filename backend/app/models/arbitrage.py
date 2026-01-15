from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ArbitrageOpportunity(Base):
    __tablename__ = "arbitrage_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String, index=True)        # BTC, ETH тощо
    target_currency = Column(String, index=True)      # USDT, USD тощо
    exchange_from = Column(String)                    # Binance, Coinbase
    exchange_to = Column(String)                      # Kraken, KuCoin
    price_from = Column(Float)                        # Ціна на exchange_from
    price_to = Column(Float)                          # Ціна на exchange_to
    price_difference = Column(Float)                  # Різниця в %
    volume_24h = Column(Float)                        # Обсяг торгів
    trust_score = Column(Float)                       # Оцінка надійності 0-1
    potential_profit = Column(Float)                  # Потенційний прибуток після комісій
    is_opportunity = Column(Boolean, default=True)    # Чарс реальна можливість
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Arbitrage {self.base_currency}/{self.target_currency} {self.price_difference}%>"