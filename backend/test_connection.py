import sys
sys.path.append('.')
from app.futures.models.exchange_connector import ExchangeConnector

# Тест 1: Перевірка читання ключів
connector = ExchangeConnector()
print("✅ ExchangeConnector створено")

# Тест 2: Отримання балансу (для перевірки ключів)
try:
    balance = connector.exchange.fetch_balance()
    print(f"✅ Баланс отримано. USDT: {balance['USDT']['free']}")
except Exception as e:
    print(f"❌ Помилка балансу: {e}")

# Тест 3: Отримання ринкових даних
try:
    ticker = connector.exchange.fetch_ticker('BTC/USDT:USDT')
    print(f"✅ Дані ринку: {ticker['symbol']} - {ticker['last']}")
except Exception as e:
    print(f"⚠️  Помилка ринкових даних (але це нормально для демо): {e}")