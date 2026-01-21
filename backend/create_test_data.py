#!/usr/bin/env python3
"""Створення тестових даних для ф'ючерсів"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.futures.models import Signal
from datetime import datetime

def create_test_signal():
    """Створити тестовий сигнал в БД"""
    db = SessionLocal()
    
    try:
        # Створюємо тестовий сигнал
        signal = Signal(
            symbol="BTCUSDT",
            direction="long",
            timeframe="1h",
            entry_price=42150.75,
            take_profit=44000.0,
            stop_loss=41500.0,
            confidence=0.78,
            reasoning_weights={
                "trend_strength": 0.8,
                "volume_confirmation": 0.7,
                "support_resistance": 0.9,
                "volatility": 0.5,
                "momentum": 0.75
            },
            explanation_text="AI виявив пробій рівня підтримки з підтвердженням обсягів",
            is_active=True
        )
        
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        print(f"✅ Тестовий сигнал створено:")
        print(f"   ID: {signal.id}")
        print(f"   Symbol: {signal.symbol}")
        print(f"   Direction: {signal.direction}")
        print(f"   Confidence: {signal.confidence}")
        
        return signal.id
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def check_tables():
    """Перевірити чи таблиці існують"""
    db = SessionLocal()
    try:
        from sqlalchemy import text
        
        # Перевіряємо таблицю сигналів
        result = db.execute(text("SELECT COUNT(*) FROM futures_signals"))
        count = result.scalar()
        print(f"📊 У таблиці futures_signals: {count} записів")
        
        # Перевіряємо таблицю віртуальних угод
        result = db.execute(text("SELECT COUNT(*) FROM virtual_trades"))
        count = result.scalar()
        print(f"📊 У таблиці virtual_trades: {count} записів")
        
    except Exception as e:
        print(f"⚠️  Таблиці ще не створені або помилка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Створення тестових даних для ф'ючерсів ===")
    check_tables()
    signal_id = create_test_signal()
    
    if signal_id:
        print(f"\n💡 Використовуй ID {signal_id} для тестування віртуальних угод")
        print(f"   Приклад: http://localhost:5000/api/futures/virtual-trades?signal_id={signal_id}")