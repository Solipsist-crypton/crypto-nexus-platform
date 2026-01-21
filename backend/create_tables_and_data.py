#!/usr/bin/env python3
"""Створення таблиць та тестових даних одним скриптом"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, engine
from app.futures.models import Signal, VirtualTrade
from sqlalchemy.orm import Session

print("=== Створення таблиць ф'ючерсів ===")

# 1. Створюємо таблиці
print("1. Створюємо таблиці...")
Base.metadata.create_all(bind=engine, tables=[Signal.__table__, VirtualTrade.__table__])
print("   ✅ Таблиці створені")

# 2. Створюємо тестовий сигнал
print("\n2. Створюємо тестовий сигнал...")
db = Session(bind=engine)

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

print(f"   ✅ Сигнал створено: ID {signal.id}")
print(f"   {signal.symbol} {signal.direction} (confidence: {signal.confidence})")

# 3. Створюємо тестову віртуальну угоду
print("\n3. Створюємо тестову віртуальну угоду...")

virtual_trade = VirtualTrade(
    signal_id=signal.id,
    entry_price=42150.0,
    current_price=42150.0,
    take_profit=44000.0,
    stop_loss=41500.0,
    status="active",
    pnl_percentage=0.0,
    pnl_amount=0.0
)

db.add(virtual_trade)
db.commit()
db.refresh(virtual_trade)

print(f"   ✅ Віртуальна угода створена: ID {virtual_trade.id}")
print(f"   Статус: {virtual_trade.status}, PnL: {virtual_trade.pnl_percentage}%")

db.close()

print("\n=== Готово! ===")
print(f"📊 Сигнал ID: {signal.id}")
print(f"📊 VirtualTrade ID: {virtual_trade.id}")
print(f"\n💡 Тестуй API:")
print(f"   GET  http://localhost:5000/api/futures/virtual-trades")
print(f"   POST http://localhost:5000/api/futures/virtual-trades/{virtual_trade.id}/update-price?current_price=42500")