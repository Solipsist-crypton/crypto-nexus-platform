# backend/test_trade_executor_fixed.py
import sys
sys.path.append('.')
from app.futures.services.trade_executor import VirtualTradeExecutor

print("🧪 ТЕСТ TRADE EXECUTOR ПІСЛЯ ФІКСУ")
print("=" * 50)

try:
    executor = VirtualTradeExecutor()
    print(f"✅ VirtualTradeExecutor створено успішно!")
    print(f"   Exchange: {executor.exchange}")
    print(f"   Logger: {executor.logger}")
    
    # Тестуємо отримання ціни
    print("\n🔍 Тестуємо отримання ціни...")
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    # Створюємо тестову угоду
    from app.futures.models import Signal
    
    # Знаходимо або створюємо сигнал
    signal = db.query(Signal).first()
    if not signal:
        print("📝 Створюємо тестовий сигнал...")
        signal = Signal(
            symbol="BTCUSDT",  # БЕЗ :USDT!
            direction="long",
            entry_price=50000.0,
            take_profit=52000.0,
            stop_loss=49000.0,
            confidence=0.8,
            timeframe="1h",
            is_active=True
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
    
    print(f"📊 Використовуємо сигнал: {signal.symbol}")
    
    # Тестуємо створення угоди
    trade = executor.create_virtual_trade(db, signal.id, 1)
    if trade:
        print(f"✅ Створено угоду #{trade.id}")
        
        # Тестуємо оновлення ціни
        result = executor.update_trade_prices(db, trade.id)
        if result:
            print(f"💰 Ціна оновлена: ${result['price_updated']}")
            print(f"📊 PnL: {result['trade']['pnl_percentage']}%")
        else:
            print("⚠️ Не вдалося оновити ціну")
    else:
        print("❌ Не вдалося створити угоду")
    
    db.close()
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ ТЕСТ ЗАВЕРШЕНО")