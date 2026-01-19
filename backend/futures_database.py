from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Використовуємо окремий файл бази даних для ф’ючерсних сигналів
DATABASE_URL = os.getenv("FUTURES_DB_URL", "sqlite:///./futures_signals.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Поставте True для відладки SQL-запитів
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Окремий Base для ф’ючерсних моделей. Це ключ до незалежності.
FuturesBase = declarative_base()

def get_futures_db():
    """Залежність для FastAPI, яка повертає сесію для роботи з ф’ючерсною БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()