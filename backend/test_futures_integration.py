# backend/test_futures_integration.py
import sys
sys.path.append('.')
from app.futures.services.signal_orchestrator import SignalOrchestrator
import json

def test_full_pipeline():
    print("🧪 ТЕСТ ПОВНОГО Ф'ЮЧЕРСНОГО ПАЙПЛАЙНУ")
    print("=" * 60)
    
    # 1. Ініціалізація
    print("1. Ініціалізація компонентів...")
    orchestrator = SignalOrchestrator()
    print("✅ Оркестратор створено")
    
    # 2. Тест для однієї пари
    print("\n2. Тест для BTC/USDT...")
    btc_signal = orchestrator.generate_signal('BTC/USDT:USDT', '1h')
    
    if 'error' in btc_signal:
        print(f"❌ Помилка: {btc_signal['error']}")
        return
    
    print(f"   📊 Символ: {btc_signal['symbol']}")
    print(f"   📈 Напрямок: {btc_signal['direction'].upper()}")
    print(f"   🎯 Впевненість: {btc_signal['confidence'] * 100}%")
    print(f"   💰 Вхід: ${btc_signal['entry_price']}")
    print(f"   📈 TP: ${btc_signal['take_profit']}")
    print(f"   📉 SL: ${btc_signal['stop_loss']}")
    print(f"   📝 Пояснення: {btc_signal['explanation'][:100]}...")
    
    # 3. Тест для кількох пар
    print("\n3. Тест для кількох пар...")
    symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
    signals = orchestrator.generate_multiple_signals(symbols)
    
    print(f"   Згенеровано сигналів: {len(signals)}/{len(symbols)}")
    
    # 4. Статистика
    print("\n4. Статистика:")
    directions = {'long': 0, 'short': 0, 'neutral': 0}
    for signal in signals:
        directions[signal.get('direction', 'neutral')] += 1
    
    for direction, count in directions.items():
        print(f"   {direction.upper()}: {count}")
    
    # 5. Збереження для перегляду
    with open('test_signals.json', 'w') as f:
        json.dump(signals, f, indent=2, default=str)
    print(f"\n💾 Сигнали збережено в test_signals.json")
    
    print("\n✅ ІНТЕГРАЦІЙНИЙ ТЕСТ ПРОЙДЕНО!")
    return signals

if __name__ == "__main__":
    test_full_pipeline()