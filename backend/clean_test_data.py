# backend/clean_test_data.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.futures.models import VirtualTrade, Signal

print("🧹 ОЧИЩЕННЯ ТЕСТОВИХ ДАНИХ")
print("=" * 50)

db = SessionLocal()

try:
    # 1. Видаляємо тестові віртуальні угоди
    test_trades = db.query(VirtualTrade).filter(
        VirtualTrade.symbol.like('%TEST%')
    ).all()
    
    if test_trades:
        for trade in test_trades:
            db.delete(trade)
        db.commit()
        print(f"✅ Видалено {len(test_trades)} тестових угод")
    
    # 2. Видаляємо тестові сигнали
    test_signals = db.query(Signal).filter(
        Signal.symbol.like('%TEST%')
    ).all()
    
    if test_signals:
        for signal in test_signals:
            db.delete(signal)
        db.commit()
        print(f"✅ Видалено {len(test_signals)} тестових сигналів")
    
    # 3. Перевіряємо що залишилось
    real_signals = db.query(Signal).filter(
        ~Signal.symbol.like('%TEST%')
    ).all()
    
    print(f"\n📊 РЕАЛЬНІ СИГНАЛИ ({len(real_signals)}):")
    for signal in real_signals[:5]:  # Перші 5
        print(f"   📈 {signal.id}: {signal.symbol} ({signal.direction}) - {signal.confidence*100}%")
    
    if len(real_signals) > 5:
        print(f"   ... та ще {len(real_signals) - 5} сигналів")
    
    # 4. Створюємо реальні віртуальні угоди з AI сигналів
    print("\n🎯 СТВОРЕННЯ ВІРТУАЛЬНИХ УГОД З AI СИГНАЛІВ:")
    
    created_count = 0
    for signal in real_signals:
        if signal.confidence >= 0.7:  # Тільки впевнені сигнали
            # Перевіряємо чи вже є угода для цього сигналу
            existing = db.query(VirtualTrade).filter(
                VirtualTrade.signal_id == signal.id
            ).first()
            
            if not existing:
                # Створюємо нову віртуальну угоду
                trade = VirtualTrade(
                    signal_id=signal.id,
                    user_id=1,
                    symbol=signal.symbol.replace('/USDT:USDT', 'USDT'),  # Конвертуємо для Binance
                    direction=signal.direction,
                    entry_price=signal.entry_price,
                    take_profit=signal.take_profit,
                    stop_loss=signal.stop_loss,
                    current_price=signal.entry_price,
                    status="active"
                )
                db.add(trade)
                created_count += 1
                print(f"   ✅ Створено угоду для {signal.symbol}")
    
    if created_count > 0:
        db.commit()
        print(f"\n🎯 Створено {created_count} реальних віртуальних угод!")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ ОЧИЩЕННЯ ЗАВЕРШЕНО")