# backend/test_virtual_fix.py
import sys
sys.path.append('.')
from app.database import SessionLocal, engine
from app.futures.models.virtual_trade import VirtualTrade as VT
from app.futures.models.signal import Signal
from sqlalchemy import inspect

# 1. Перевірка чи існують таблиці
inspector = inspect(engine)
tables = inspector.get_table_names()
print("📊 Таблиці в базі даних:")
for table in tables:
    print(f"   - {table}")

# 2. Створення таблиць якщо потрібно
if 'virtual_trades' not in tables:
    print("🔧 Створюємо таблицю virtual_trades...")
    VT.__table__.create(engine)
    
if 'futures_signals' not in tables:
    print("🔧 Створюємо таблицю futures_signals...")
    Signal.__table__.create(engine)

# 3. Простий тест
db = SessionLocal()

try:
    # Створюємо тестовий сигнал
    test_signal = Signal(
        symbol="TEST/USDT:USDT",
        direction="long",
        confidence=0.85,
        entry_price=1000.0,
        take_profit=1100.0,
        stop_loss=950.0,
        timeframe="1h",
        is_active=True,
        reasoning_weights={"test": 1.0},
        explanation_text="Test signal"
    )
    db.add(test_signal)
    db.commit()
    db.refresh(test_signal)
    
    print(f"✅ Тестовий сигнал створено ID: {test_signal.id}")
    
    # Створюємо тестову угоду
    test_trade = VT(
        signal_id=test_signal.id,
        user_id=1,
        symbol="TEST/USDT:USDT",
        direction="long",
        entry_price=1000.0,
        take_profit=1100.0,
        stop_loss=950.0,
        current_price=1000.0,
        status="active"
    )
    db.add(test_trade)
    db.commit()
    db.refresh(test_trade)
    
    print(f"✅ Тестова угода створено ID: {test_trade.id}")
    
    # Перевіряємо зв'язок
    print(f"🔗 Перевірка зв'язку...")
    print(f"   Signal ID у trade: {test_trade.signal_id}")
    print(f"   Trade ID у signal: {len(test_signal.virtual_trades) if hasattr(test_signal, 'virtual_trades') else 'No attr'}")
    
    # Тестуємо calculate_pnl
    test_trade.calculate_pnl(1050.0)
    db.commit()
    
    print(f"💰 PnL при ціні $1050: {test_trade.pnl_percentage}%")
    print(f"📊 Статус: {test_trade.status}")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n✅ ТЕСТ ЗАВЕРШЕНО")