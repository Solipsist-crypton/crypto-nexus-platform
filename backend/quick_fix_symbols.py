# backend/quick_fix_symbols.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.futures.models import VirtualTrade, Signal

print("🔧 ШВИДКИЙ ФІКС СИМВОЛІВ")
print("=" * 50)

def normalize_symbol(symbol: str) -> str:
    """Швидка функція нормалізації"""
    symbol = symbol.upper().replace('/', '').replace(':USDT', '')
    if not symbol.endswith('USDT'):
        symbol += 'USDT'
    return symbol

db = SessionLocal()

try:
    # 1. Фіксимо сигнали
    signals = db.query(Signal).all()
    print(f"📊 Знайдено {len(signals)} сигналів")
    
    for signal in signals:
        old_symbol = signal.symbol
        new_symbol = normalize_symbol(old_symbol)
        
        if old_symbol != new_symbol:
            signal.symbol = new_symbol
            print(f"  🔄 {old_symbol} → {new_symbol}")
    
    # 2. Фіксимо віртуальні угоди
    trades = db.query(VirtualTrade).all()
    print(f"\n📊 Знайдено {len(trades)} віртуальних угод")
    
    for trade in trades:
        old_symbol = trade.symbol
        new_symbol = normalize_symbol(old_symbol)
        
        if old_symbol != new_symbol:
            trade.symbol = new_symbol
            print(f"  🔄 {old_symbol} → {new_symbol}")
    
    # Зберігаємо зміни
    db.commit()
    print(f"\n✅ Усі символи оновлено!")
    
    # Перевірка
    print("\n📋 ПЕРЕВІРКА:")
    for signal in db.query(Signal).limit(3).all():
        print(f"  📈 {signal.id}: {signal.symbol}")
    
    for trade in db.query(VirtualTrade).limit(3).all():
        print(f"  💰 {trade.id}: {trade.symbol}")
        
except Exception as e:
    print(f"❌ Помилка: {e}")
    db.rollback()
finally:
    db.close()