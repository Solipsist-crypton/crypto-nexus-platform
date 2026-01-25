print("🔧 ФІКС ДЛЯ ФАЗИ 2 (VIRTUAL TRADING)")
print("=" * 50)

import sys
sys.path.append('.')

# Перевіряємо поточний exchange_connector
try:
    from app.futures.models.exchange_connector import ExchangeConnector
    
    exchange = ExchangeConnector()
    
    # Тестуємо різні формати
    test_cases = [
        ("BTCUSDT", "BTCUSDT"),
        ("ETH/USDT:USDT", "ETHUSDT"),
        ("BTC/USDT", "BTCUSDT"),
    ]
    
    print("🧪 Тестуємо конвертацію:")
    for input_sym, expected in test_cases:
        try:
            # Викликаємо fetch_ticker
            result = exchange.fetch_ticker(input_sym)
            if result:
                print(f"  ✅ {input_sym:20} → {result['symbol']:20} Ціна: ${result['last']}")
            else:
                print(f"  ❌ {input_sym:20} → Немає даних")
        except Exception as e:
            print(f"  ❌ {input_sym:20} → Помилка: {str(e)[:50]}")
            
except ImportError as e:
    print(f"❌ Не вдалося імпортувати: {e}")

print("\n📝 ШВИДКИЙ ФІКС:")
print("1. Відкрийте файл: backend/app/futures/services/exchange_connector.py")
print("2. Знайдіть метод fetch_ticker")
print("3. Переконайтеся, що символ НЕ перетворюється на '...:USDT'")
print("4. Символ має бути без :USDT на кінці")