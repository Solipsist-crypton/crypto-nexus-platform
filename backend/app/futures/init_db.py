"""
Скрипт для створення таблиць ф'ючерсів.
Запустити: python -m app.futures.init_db
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine
from app.database import Base
from app.futures.models import Signal, VirtualTrade

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
        tables = [Signal.__table__, VirtualTrade.__table__]
        Base.metadata.create_all(bind=engine, tables=tables)
        
        print("✅ Таблиці ф'ючерсів створені успішно!")
        print("📊 Створені таблиці:")
        print(f"  - {Signal.__tablename__} ({len(Signal.__table__.columns)} колонок)")
        print(f"  - {VirtualTrade.__tablename__} ({len(VirtualTrade.__table__.columns)} колонок)")
        
        # Показуємо колонки
        print("\n📋 Колонки Signal:")
        for column in Signal.__table__.columns:
            print(f"  • {column.name}: {column.type}")
            
        print("\n📋 Колонки VirtualTrade:")
        for column in VirtualTrade.__table__.columns:
            print(f"  • {column.name}: {column.type}")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_futures_tables()