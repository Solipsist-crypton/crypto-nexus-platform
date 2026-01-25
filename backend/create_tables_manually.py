# backend/create_tables_manually.py
import sys
sys.path.append('.')
from app.database import engine, Base
from app.futures.models.signal import Signal
from app.futures.models.virtual_trade import VirtualTrade

print("📦 Створення таблиць...")
Base.metadata.create_all(bind=engine)
print("✅ Всі таблиці створено!")