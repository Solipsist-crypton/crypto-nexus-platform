from fastapi import APIRouter
from datetime import datetime
from app.futures.services.explanation_builder import explanation_builder
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
@router.post("/signals/generate")
def generate_signal():
    """Згенерувати тестовий AI-сигнал з поясненням"""
    # Симулюємо AI-фактори
    factors = {
        "trend_strength": round(random.uniform(0.5, 0.9), 2),
        "volume_confirmation": round(random.uniform(0.4, 0.8), 2),
        "support_resistance": round(random.uniform(0.6, 0.95), 2),
        "volatility": round(random.uniform(0.3, 0.7), 2),
        "momentum": round(random.uniform(0.5, 0.85), 2),
        "market_sentiment": round(random.uniform(0.4, 0.8), 2)
    }
    
    confidence = round(random.uniform(0.6, 0.95), 2)
    direction = random.choice(["long", "short"])
    
    # Генеруємо пояснення
    explanation = explanation_builder.build_explanation(
        symbol="BTCUSDT",
        direction=direction,
        confidence=confidence,
        factors=factors
    )
    
    return {
        "status": "success",
        "signal": {
            "symbol": "BTCUSDT",
            "direction": direction,
            "confidence": confidence,
            "explanation": explanation,
            "factors": factors,
            "entry_price": round(42000 + random.uniform(-1000, 1000), 2),
            "take_profit": round(44000 + random.uniform(-2000, 2000), 2),
            "stop_loss": round(41000 + random.uniform(-2000, 2000), 2),
            "timestamp": datetime.now().isoformat()
        },
        "module": "futures_v1"
    }

@router.get("/explain")
def explain_signal(
    symbol: str = "BTCUSDT",
    direction: str = "long",
    confidence: float = 0.75
):
    """Отримати текстове пояснення для сигналу"""
    explanation = explanation_builder.build_explanation(
        symbol=symbol,
        direction=direction,
        confidence=confidence
    )
    
    return {
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "explanation": explanation,
        "timestamp": datetime.now().isoformat()
    }