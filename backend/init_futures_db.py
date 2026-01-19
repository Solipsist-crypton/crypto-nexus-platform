#!/usr/bin/env python3
"""
Скрипт для створення окремої бази даних та таблиць для ф’ючерсного модуля.
Запуск: docker-compose exec backend python init_futures_db.py
"""
import sys
sys.path.append('.')

from backend.futures_database import engine, FuturesBase
import backend.futures_models  # Імпорт модуля з моделями для їх реєстрації

def init_futures_database():
    print("🔄 Ініціалізація окремої бази даних для ф’ючерсних сигналів...")
    try:
        # Створюємо ВСІ таблиці, які успадковані від FuturesBase
        FuturesBase.metadata.create_all(bind=engine)
        print("✅ Базу даних та таблиці для ф’ючерсів успішно створено!")
        print(f"   Файл бази даних: futures_signals.db")
        print("   Створені таблиці: signals, virtual_trades")
    except Exception as e:
        print(f"❌ Помилка ініціалізації: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_futures_database()