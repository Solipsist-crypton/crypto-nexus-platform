# backend/test_celery_simple.py
import sys
sys.path.append('.')
from app.celery_app import celery_app

print("🧪 ТЕСТ CELERY БЕЗ WORKER")
print("=" * 50)

# Просто перевіряємо чи Celery app створюється
print(f"✅ Celery app створено: {celery_app}")
print(f"🔧 Брокер: {celery_app.conf.broker_url}")
print(f"📋 Завдання: {list(celery_app.tasks.keys())}")

# Тест симуляції завдання
print("\n🧪 СИМУЛЯЦІЯ ЗАВДАННЯ...")

# Імпортуємо модуль для прямого виклику
from app.futures.tasks import update_virtual_trades_prices

# Викликаємо без Celery (синхронно)
try:
    result = update_virtual_trades_prices()
    print(f"📊 Результат: {result}")
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ ТЕСТ ЗАВЕРШЕНО")