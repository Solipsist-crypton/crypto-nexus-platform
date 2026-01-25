# backend/test_virtual_trading.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.futures.models import Signal
from app.futures.services.trade_executor import VirtualTradeExecutor
from datetime import datetime

def test_virtual_trading():
    print("🧪 ТЕСТ ВІРТУАЛЬНОЇ ТОРГІВЛІ")
    print("=" * 50)
    
    db = SessionLocal()
    executor = VirtualTradeExecutor()
    
    try:
        # 1. Знаходимо останній сигнал
        signal = db.query(Signal).order_by(Signal.created_at.desc()).first()
        
        if not signal:
            print("❌ Немає сигналів для тестування")
            return
        
        print(f"📊 Тестуємо сигнал: {signal.symbol} ({signal.direction})")
        
        # 2. Створюємо віртуальну угоду
        trade = executor.create_virtual_trade(db, signal.id, user_id=1)
        
        if trade:
            print(f"✅ Створено віртуальну угоду #{trade.id}")
            print(f"   Символ: {trade.symbol}")
            print(f"   Напрямок: {trade.direction}")
            print(f"   Вхід: ${trade.entry_price}")
            print(f"   TP: ${trade.take_profit}")
            print(f"   SL: ${trade.stop_loss}")
            
            # 3. Оновлюємо ціну
            result = executor.update_trade_prices(db, trade.id)
            
            if result:
                print(f"✅ Ціну оновлено: ${result['price_updated']}")
                print(f"   PnL: {result['trade']['pnl_percentage']}%")
                print(f"   Статус: {result['trade']['status']}")
        
        # 4. Статистика
        stats = executor.update_all_active_trades(db)
        print(f"\n📊 Статистика: {stats['updated']}/{stats['total']} оновлено")
        
    finally:
        db.close()
    
    print("\n✅ ТЕСТ ЗАВЕРШЕНО")

if __name__ == "__main__":
    test_virtual_trading()