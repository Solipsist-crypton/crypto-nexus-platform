import sys
import os

# Додаємо шлях
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing Telegram notifier...")
    
    # Спробуйте різні варіанти імпорту
    try:
        from app.services.telegram_notifier import telegram_notifier
        print("✅ Imported from app.services.telegram_notifier")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        
        # Спробуйте прямий імпорт
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "telegram_notifier", 
            "app/services/telegram_notifier.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        telegram_notifier = module.telegram_notifier
        print("✅ Imported directly")
    
    # Тест
    print(f"\nNotifier enabled: {telegram_notifier.enabled}")
    
    # Тест підключення
    print("\n1. Testing bot connection...")
    if telegram_notifier.test_connection():
        print("   ✅ Bot connected")
    else:
        print("   ❌ Bot connection failed")
    
    # Тест повідомлення
    print("\n2. Sending test message...")
    test_result = telegram_notifier.send_message(
        "🤖 *Test Message*\n\nThis is a test from crypto-nexus\n\n✅ System is working!"
    )
    print(f"   Result: {'✅ Success' if test_result else '❌ Failed'}")
    
    # Тест арбітражу
    print("\n3. Testing arbitrage alert...")
    test_opportunity = {
        'coin': 'BTC',
        'net_profit_percent': 3.75,
        'buy_exchange': 'Binance',
        'sell_exchange': 'KuCoin',
        'buy_price': 43250.75,
        'sell_price': 44890.20,
        'volume': 1500000
    }
    
    alert_result = telegram_notifier.send_arbitrage_alert(
        test_opportunity, 
        threshold_percent=1.0
    )
    print(f"   Result: {'✅ Alert sent' if alert_result else '❌ Alert failed'}")
    
except Exception as e:
    print(f"\n💥 Critical error: {e}")
    import traceback
    traceback.print_exc()