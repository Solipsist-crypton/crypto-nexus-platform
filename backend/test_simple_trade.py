# backend/test_simple_fix.py
import sys
sys.path.append('.')
from app.futures.models.exchange_connector import ExchangeConnector

print("🧪 ПРОСТИЙ ТЕСТ ПІСЛЯ ФІКСУ")
print("=" * 50)

exchange = ExchangeConnector()

# Тестуємо різні формати
test_cases = [
    "BTCUSDT",           # Чистий формат
    "BTC/USDT:USDT",     # Формат з Фази 1
    "ETHUSDT",
    "SOL/USDT:USDT",
]

print("📊 Тестуємо символи:")
for symbol in test_cases:
    try:
        ticker = exchange.fetch_ticker(symbol)
        if ticker:
            print(f"✅ {symbol:20} → ${ticker['last']:,.2f}")
        else:
            print(f"❌ {symbol:20} → Немає даних")
    except Exception as e:
        print(f"❌ {symbol:20} → Помилка: {str(e)[:50]}")

print("\n🎯 Створюємо тестову віртуальну угоду:")
try:
    from app.database import SessionLocal
    from app.futures.services.trade_executor import VirtualTradeExecutor
    from app.futures.models import Signal, VirtualTrade
    
    db = SessionLocal()
    
    # Створюємо тестовий сигнал
    test_signal = Signal(
        symbol="BTCUSDT",  # БЕЗ :USDT!
        direction="long",
        entry_price=88500.0,
        take_profit=90000.0,
        stop_loss=87000.0,
        confidence=0.8,
        timeframe="1h",
        is_active=True
    )
    db.add(test_signal)
    db.commit()
    db.refresh(test_signal)
    
    print(f"✅ Створено сигнал ID: {test_signal.id}")
    
    # Тестуємо віртуальну угоду
    executor = VirtualTradeExecutor()
    trade = executor.create_virtual_trade(db, test_signal.id, 1)
    
    if trade:
        print(f"✅ Створено угоду ID: {trade.id}")
        
        # Оновлюємо ціну
        result = executor.update_trade_prices(db, trade.id)
        
        if result:
            print(f"💰 Ціна: ${result['price_updated']:,.2f}")
            print(f"📊 PnL: {result['trade']['pnl_percentage']}%")
            print(f"🎯 Статус: {result['trade']['status']}")
    
    db.close()
    
except Exception as e:
    print(f"❌ Помилка: {e}")

print("\n✅ ТЕСТ ЗАВЕРШЕНО")