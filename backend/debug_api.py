# backend/debug_api_sql.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from sqlalchemy import text

print("🔍 ДЕБАГ SQL ЗАПИТУ API")
print("=" * 50)

db = SessionLocal()

try:
    # 1. Який запит виконує API?
    print("1. 📋 SQL запит який виконує API (/api/futures/signals):")
    
    # Емулюємо запит API
    sql = """
    SELECT id, symbol, direction, confidence, is_active, created_at 
    FROM futures_signals 
    WHERE is_active = 1 
    ORDER BY created_at DESC 
    LIMIT 10
    """
    
    result = db.execute(text(sql))
    rows = result.fetchall()
    
    print(f"   📊 Результат SQL: {len(rows)} рядків")
    for row in rows:
        print(f"      🆔 {row[0]}: {row[1]} {row[2]} active={row[4]}")
    
    # 2. Перевіримо всі сигнали без фільтрів
    print("\n2. 📋 Всі сигнали в БД:")
    sql_all = "SELECT * FROM futures_signals"
    result_all = db.execute(text(sql_all))
    all_rows = result_all.fetchall()
    
    print(f"   📊 Всього сигналів: {len(all_rows)}")
    for row in all_rows[:5]:  # Перші 5
        print(f"      🆔 {row[0]}: {row[1]} {row[2]}, active={row[13] if len(row) > 13 else 'N/A'}")
    
    # 3. Перевіримо структуру таблиці
    print("\n3. 🏗️ Структура таблиці futures_signals:")
    schema = db.execute(text("PRAGMA table_info(futures_signals)"))
    columns = schema.fetchall()
    
    for col in columns:
        print(f"      {col[1]:20} {col[2]:10} {'NULL' if col[3] else 'NOT NULL'}")
    
    # 4. Перевіримо конкретно поле is_active
    print("\n4. 🔍 Значення поля is_active:")
    for row in all_rows:
        if len(row) > 13:  # Переконуємось що є поле is_active
            print(f"      Сигнал {row[0]}: is_active = {row[13]} (тип: {type(row[13]).__name__})")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()