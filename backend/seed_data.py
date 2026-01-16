import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.arbitrage import ArbitrageOpportunity

def seed_arbitrage_data():
    """Додати тестові дані арбітражу"""
    db = SessionLocal()
    
    try:
        # Очистити попередні дані
        db.query(ArbitrageOpportunity).delete()
        
        currencies = ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX", "MATIC"]
        exchanges = ["Binance", "Coinbase", "Kraken", "KuCoin", "Bybit", "OKX"]
        
        opportunities = []
        
        for i in range(30):  # Менше записів для початку
            base = random.choice(currencies)
            exchange_from = random.choice(exchanges)
            exchange_to = random.choice([e for e in exchanges if e != exchange_from])
            
            price_from = round(random.uniform(25000, 35000), 2)
            price_to = round(price_from * (1 + random.uniform(0.002, 0.03)), 2)
            price_diff = round(((price_to - price_from) / price_from) * 100, 2)
            
            opportunity = ArbitrageOpportunity(
                base_currency=base,
                target_currency="USDT",
                exchange_from=exchange_from,
                exchange_to=exchange_to,
                price_from=price_from,
                price_to=price_to,
                price_difference=price_diff,
                volume_24h=round(random.uniform(1000000, 50000000), 2),
                trust_score=round(random.uniform(0.6, 0.95), 2),
                potential_profit=round(price_diff * 0.85, 2),
                is_opportunity=price_diff > 1.0,  # Активна, якщо різниця > 1%
                created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 72))
            )
            opportunities.append(opportunity)
        
        db.add_all(opportunities)
        db.commit()
        print(f"✅ Додано {len(opportunities)} тестових арбітражних можливостей")
        print(f"📊 Приклад: {opportunities[0].base_currency} з {price_diff}% різницею")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_arbitrage_data()