# backend/run_virtual_trading.py
import sys
import time
import schedule
from datetime import datetime
sys.path.append('.')
from app.database import SessionLocal
from app.futures.services.trade_executor import VirtualTradeExecutor

def update_all_trades():
    """Оновлення всіх активних угод"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n🕒 {timestamp} - Оновлення віртуальних угод...")
    
    db = SessionLocal()
    try:
        executor = VirtualTradeExecutor()
        results = executor.update_all_active_trades(db)
        
        if results["updated"] > 0:
            print(f"   📊 Оновлено {results['updated']}/{results['total']} угод")
            if results["tp_hit"] > 0:
                print(f"   🎯 Take Profit досягнуто: {results['tp_hit']}")
            if results["sl_hit"] > 0:
                print(f"   🛑 Stop Loss досягнуто: {results['sl_hit']}")
        else:
            print("   ℹ️ Немає активних угод")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    finally:
        db.close()

def create_test_trade():
    """Створення тестової віртуальної угоди"""
    print("\n📝 Створення тестової угоди...")
    
    db = SessionLocal()
    try:
        from app.futures.models import Signal
        from app.futures.services.trade_executor import VirtualTradeExecutor
        
        # Знаходимо останній сигнал
        signal = db.query(Signal).order_by(Signal.id.desc()).first()
        
        if signal:
            executor = VirtualTradeExecutor()
            trade = executor.create_virtual_trade(db, signal.id, user_id=1)
            
            if trade:
                print(f"   ✅ Створено угоду #{trade.id}")
                print(f"   📈 {trade.symbol} {trade.direction}")
                print(f"   💰 Вхід: ${trade.entry_price}")
                print(f"   🎯 TP: ${trade.take_profit}")
                print(f"   🛑 SL: ${trade.stop_loss}")
        
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    finally:
        db.close()

def main():
    """Головна функція віртуальної торгівлі"""
    print("🚀 ЗАПУСК СИСТЕМИ ВІРТУАЛЬНОЇ ТОРГІВЛІ")
    print("=" * 60)
    print("📊 Фаза 2: Тестування AI сигналів без ризику")
    print("⏰ Оновлення кожні 30 секунд")
    print("🛑 Ctrl+C для зупинки")
    print("-" * 60)
    
    # Створюємо тестову угоду
    create_test_trade()
    
    # Перше оновлення
    update_all_trades()
    
    # Налаштовуємо розклад
    schedule.every(30).seconds.do(update_all_trades)
    
    # Запускаємо також створення нових угод кожні 5 хвилин
    schedule.every(5).minutes.do(create_test_trade)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Система віртуальної торгівлі зупинена")
        print("📊 Переходимо до наступних кроків...")

if __name__ == "__main__":
    main()