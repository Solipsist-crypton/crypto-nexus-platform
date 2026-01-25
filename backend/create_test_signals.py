# backend/create_test_signals.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.futures.models import Signal
from datetime import datetime

print("📝 СТВОРЕННЯ ТЕСТОВИХ СИГНАЛІВ")
print("=" * 50)

db = SessionLocal()

try:
    # Перевіримо чи є сигнали
    existing = db.query(Signal).count()
    print(f"📊 Поточних сигналів: {existing}")
    
    if existing == 0:
        # Створимо тестові сигнали
        test_signals = [
            {
                "symbol": "BTC/USDT:USDT",
                "direction": "long",
                "confidence": 0.85,
                "entry_price": 88500.0,
                "take_profit": 90000.0,
                "stop_loss": 87000.0,
                "timeframe": "1h",
                "reasoning_weights": {"ta": 0.7, "sentiment": 0.3},
                "explanation_text": "Strong bullish momentum on 1h timeframe"
            },
            {
                "symbol": "ETH/USDT:USDT",
                "direction": "short",
                "confidence": 0.75,
                "entry_price": 2935.0,
                "take_profit": 2880.0,
                "stop_loss": 2980.0,
                "timeframe": "1h",
                "reasoning_weights": {"ta": 0.6, "sentiment": 0.4},
                "explanation_text": "Resistance level holding on ETH"
            },
            {
                "symbol": "SOL/USDT:USDT",
                "direction": "long",
                "confidence": 0.9,
                "entry_price": 126.5,
                "take_profit": 135.0,
                "stop_loss": 120.0,
                "timeframe": "4h",
                "reasoning_weights": {"ta": 0.8, "sentiment": 0.2},
                "explanation_text": "Breakout confirmation on SOL"
            }
        ]
        
        for signal_data in test_signals:
            signal = Signal(
                **signal_data,
                is_active=True,
                source="ai_v1"
            )
            db.add(signal)
        
        db.commit()
        print(f"✅ Створено {len(test_signals)} тестових сигналів")
    
    # Показати що є
    signals = db.query(Signal).all()
    print(f"\n📋 СИГНАЛИ В БАЗІ ({len(signals)}):")
    for signal in signals:
        print(f"   📈 {signal.id}: {signal.symbol} {signal.direction.upper()} ({signal.confidence*100:.0f}%)")
        
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ ГОТОВО")