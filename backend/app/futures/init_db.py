"""
ОКРЕМИЙ скрипт для створення таблиць ф'ючерсів.
Не чіпає основну БД, поки ми явно не викликаємо цей скрипт.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine
from backend.app.futures.models.base import FuturesBase
from backend.app.futures.models.signal import Signal

def init_futures_tables():
    """Створює таблиці для ф'ючерсів"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не знайдено")
        return
    
    print(f"🔗 Підключаємось до: {database_url}")
    
    try:
        engine = create_engine(database_url)
        
        # Створюємо ТІЛЬКИ таблиці ф'ючерсів
        FuturesBase.metadata.create_all(bind=engine)
        
        print("✅ Таблиці ф'ючерсів створено успішно!")
        print("📊 Створені таблиці:", list(FuturesBase.metadata.tables.keys()))
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    init_futures_tables()