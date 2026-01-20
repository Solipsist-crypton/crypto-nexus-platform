"""
Скрипт для створення таблиць ф'ючерсів.
Запустити: python -m app.futures.init_db
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine
from backend.app.database import Base
from backend.app.futures.models import Signal

def init_futures_tables():
    """Створює таблиці для ф'ючерсів"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не знайдено")
        return
    
    print(f"🔗 Підключаємось до: {database_url}")
    
    try:
        engine = create_engine(database_url)
        
        # Створюємо таблиці
        Base.metadata.create_all(bind=engine, tables=[Signal.__table__])
        
        print("✅ Таблиця futures_signals створена успішно!")
        print("📊 Колонки:")
        for column in Signal.__table__.columns:
            print(f"  - {column.name}: {column.type}")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_futures_tables()