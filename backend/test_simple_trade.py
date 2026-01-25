# backend/test_simple_trade.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.futures.models.signal import Signal
from app.futures.models.virtual_trade import VirtualTrade

print("🧪 ПРОСТИЙ ТЕСТ СТВОРЕННЯ УГОДИ")
print("=" * 50)

db = SessionLocal()

try:
    # 1. Знаходимо або створюємо сигнал
    signal = db.query(Signal).first()
    if not signal:
        print("📝 Створюємо тестовий сигнал...")
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
            explanation_text="Test signal for virtual trading"
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
    
    print(f"📊 Використовуємо сигнал ID: {signal.id}")
    print(f"   Symbol: {signal.symbol}")
    print(f"   Direction: {signal.direction}")
    
    # 2. Створюємо віртуальну угоду
    trade = VirtualTrade(
        signal_id=signal.id,
        user_id=1,
        symbol=signal.symbol,
        direction=signal.direction,
        entry_price=signal.entry_price,
        take_profit=signal.take_profit,
        stop_loss=signal.stop_loss,
        current_price=signal.entry_price,
        status="active",
        pnl_percentage=0.0,
        pnl_amount=0.0
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    
    print(f"✅ Віртуальна угода створена!")
    print(f"   ID: {trade.id}")
    print(f"   Symbol: {trade.symbol}")
    print(f"   Entry: ${trade.entry_price}")
    print(f"   TP: ${trade.take_profit}")
    print(f"   SL: ${trade.stop_loss}")
    
    # 3. Тестуємо calculate_pnl
    print("\n🧮 Тестуємо розрахунок PnL:")
    
    # Симулюємо зростання ціни
    new_price = 42500.0
    trade.calculate_pnl(new_price)
    db.commit()
    
    print(f"   Поточна ціна: ${new_price}")
    print(f"   PnL: {trade.pnl_percentage:.2f}%")
    print(f"   Статус: {trade.status}")
    
    # Симулюємо досягнення TP
    print("\n🎯 Тестуємо Take Profit:")
    trade.calculate_pnl(44100.0)
    db.commit()
    print(f"   Ціна: $44100.0")
    print(f"   Статус: {trade.status}")
    print(f"   PnL: {trade.pnl_percentage:.2f}%")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n✅ ТЕСТ ЗАВЕРШЕНО")