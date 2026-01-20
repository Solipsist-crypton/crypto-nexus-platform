import os
from dataclasses import dataclass

@dataclass
class FuturesConfig:
    """Конфігурація для модуля ф'ючерсів"""
    # Використовуємо ТУ Ж БД, але окремі таблиці
    database_url = os.getenv("DATABASE_URL")
    
    # Налаштування AI (тимчасові)
    ai_model_path = "models/futures_ai_v1.pkl"
    min_confidence = 0.65  # Мінімальний confidence для сигналу
    
config = FuturesConfig()