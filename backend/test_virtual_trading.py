# backend/test_real_trading.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.futures.models import Signal
from app.futures.services.trade_executor import VirtualTradeExecutor

print("🧪 ТЕСТ РЕАЛЬНОЇ ВІРТУАЛЬНОЇ ТОРГІВЛІ")
print("=" * 50)

db = SessionLocal()
executor = VirtualTradeExecutor()

try:
    # 1. Знаходимо або створюємо реальний сигнал
    signal = db.query(Signal).filter(Signal.symbol.like('BTC%')).first()
    
    if not signal:
        print("📝 Створюємо реальний сигнал BTCUSDT...")
        signal = Signal(
            symbol="BTCUSDT",
            direction="long",
            confidence=0.85,
            entry_price=42150.75,
            take_profit=44000.0,
            stop_loss=41500.0,
            timeframe="1h",
            is_active=True,
            reasoning_weights={"ta": 0.6, "sentiment": 0.4},
            explanation_text="Real BTC signal for testing"
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
    
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
        
        # 3. Оновлюємо ціну (реальна ціна з Binance)
        result = executor.update_trade_prices(db, trade.id)
        
        if result:
            print(f"✅ Ціну оновлено: ${result['price_updated']}")
            print(f"   PnL: {result['trade']['pnl_percentage']}%")
            print(f"   Статус: {result['trade']['status']}")
        else:
            print("⚠️ Не вдалося оновити ціну")
    
    # 4. Статистика
    stats = executor.update_all_active_trades(db)
    print(f"\n📊 Статистика оновлення:")
    print(f"   Усього активних: {stats['total']}")
    print(f"   Оновлено: {stats['updated']}")
    print(f"   TP досягнуто: {stats['tp_hit']}")
    print(f"   SL досягнуто: {stats['sl_hit']}")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n✅ ТЕСТ ЗАВЕРШЕНО")