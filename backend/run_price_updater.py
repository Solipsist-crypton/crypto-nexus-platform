# backend/run_price_updater.py
import sys
import time
import schedule
sys.path.append('.')
from app.database import SessionLocal
from app.futures.services.trade_executor import VirtualTradeExecutor

def update_prices():
    """Функція оновлення цін"""
    print(f"\n🕒 {time.strftime('%H:%M:%S')} - Оновлення цін...")
    
    db = SessionLocal()
    try:
        executor = VirtualTradeExecutor()
        results = executor.update_all_active_trades(db)
        
        if results["updated"] > 0:
            print(f"   📊 Оновлено {results['updated']}/{results['total']} угод")
            if results["tp_hit"] > 0:
                print(f"   🎯 Take Profit: {results['tp_hit']}")
            if results["sl_hit"] > 0:
                print(f"   🛑 Stop Loss: {results['sl_hit']}")
        else:
            print("   ℹ️ Немає активних угод для оновлення")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    finally:
        db.close()

def main():
    """Головна функція оновлювача"""
    print("🚀 ЗАПУСК ПРОСТОГО ОНОВЛЮВАЧА ЦІН")
    print("=" * 50)
    print("📝 Оновлення кожні 30 секунд")
    print("🛑 Ctrl+C для зупинки")
    print("-" * 50)
    
    # Перше оновлення
    update_prices()
    
    # Налаштовуємо розклад
    schedule.every(30).seconds.do(update_prices)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Оновлювач зупинено")

if __name__ == "__main__":
    main()