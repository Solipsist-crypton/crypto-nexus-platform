# backend/reset_virtual_trades.py
import sys
sys.path.append('.')
from app.database import engine
from sqlalchemy import text

print("🔄 Скидання таблиці virtual_trades...")

# Видаляємо стару таблицю
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS virtual_trades"))
    conn.commit()

print("✅ Стара таблиця видалена")

# Імпортуємо моделі для створення нової таблиці
from app.futures.models.virtual_trade import VirtualTrade
from app.futures.models.signal import Signal

# Створюємо нову таблицю з правильною структурою
VirtualTrade.__table__.create(engine)
print("✅ Нова таблиця створена з правильною структурою")

# Перевіряємо
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(virtual_trades)"))
    columns = result.fetchall()
    
print("\n📊 Структура таблиці virtual_trades:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")