from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter(tags=["futures"])  # БЕЗ prefix тут

@router.get("/health")
def health_check():
    """Проста перевірка роботи модуля ф'ючерсів"""
    return {
        "module": "futures_signals",
        "status": "active",
        "version": "0.0.1",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/test")
def test_endpoint():
    """Тестовий ендпоінт"""
    return {
        "message": "Futures module is working",
        "test_data": {
            "signal": "BTCUSDT LONG",
            "confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        }
    }