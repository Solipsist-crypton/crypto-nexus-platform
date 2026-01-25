# backend/app/celery_app.py
from celery import Celery
import os

# Використовуємо Redis як брокер
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Створюємо Celery app
celery_app = Celery(
    'crypto_nexus',
    broker=redis_url,
    backend=redis_url,
    include=[
        'app.futures.tasks',
        # Додавайте інші модулі з tasks тут
    ]
)

# Налаштування
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
)

# Розклад завдань
celery_app.conf.beat_schedule = {
    'update-virtual-trades-every-minute': {
        'task': 'app.futures.tasks.update_virtual_trades_prices',
        'schedule': 60.0,  # кожну хвилину
    },
}