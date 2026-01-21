import requests
import json

BASE_URL = "http://localhost:5000/api/futures"

def test_virtual_trades():
    print("=== Testing Virtual Trades API ===\n")
    
    # 1. Створимо тестовий сигнал спочатку
    print("1. Creating test signal...")
    signal_data = {
        "symbol": "BTCUSDT",
        "direction": "long",
        "confidence": 0.75,
        "entry_price": 42000.0,
        "take_profit": 44000.0,
        "stop_loss": 41000.0,
        "explanation_text": "Test signal for virtual trading"
    }
    
    # Спочатку потрібно мати сигнал в БД
    # Тимчасово використаємо ID 1 (якщо є)
    signal_id = 1
    
    # 2. Створити віртуальну угоду
    print(f"\n2. Creating virtual trade for signal {signal_id}...")
    response = requests.post(
        f"{BASE_URL}/virtual-trades",
        params={
            "signal_id": signal_id,
            "entry_price": 42150.0,
            "take_profit": 44000.0,
            "stop_loss": 41500.0
        }
    )
    
    if response.status_code == 200:
        trade_data = response.json()
        trade_id = trade_data["trade"]["id"]
        print(f"   ✅ Virtual trade created: ID {trade_id}")
        print(f"   Status: {trade_data['trade']['status']}")
        print(f"   Entry: ${trade_data['trade']['entry_price']}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.text}")
        return
    
    # 3. Отримати список угод
    print("\n3. Getting all virtual trades...")
    response = requests.get(f"{BASE_URL}/virtual-trades")
    if response.status_code == 200:
        trades_data = response.json()
        print(f"   ✅ Found {trades_data['count']} trades")
    
    # 4. Оновити ціну (симуляція руху ринку)
    print("\n4. Updating trade price...")
    
    # Тестуємо різні сценарії
    test_prices = [
        42200.0,  # Малий плюс
        42500.0,  # +1.5%
        43000.0,  # +2.5%
        43500.0,  # +3.2%
        44050.0,  # TP досягнуто!
    ]
    
    for i, price in enumerate(test_prices):
        print(f"\n   Step {i+1}: Price ${price}")
        response = requests.post(
            f"{BASE_URL}/virtual-trades/{trade_id}/update-price",
            params={"current_price": price}
        )
        
        if response.status_code == 200:
            update_data = response.json()
            print(f"     PnL: {update_data['pnl_update']['pnl_percentage']:.2f}%")
            print(f"     Status: {update_data['trade']['status']}")
            
            if update_data['trade']['status'] != 'active':
                print(f"     🎯 Trade closed: {update_data['trade']['status']}")
                break
        else:
            print(f"     ❌ Error: {response.text}")
    
    # 5. Отримати деталі угоди
    print("\n5. Getting trade details...")
    response = requests.get(f"{BASE_URL}/virtual-trades/{trade_id}")
    if response.status_code == 200:
        trade_details = response.json()
        print(f"   Final PnL: {trade_details['trade']['pnl_percentage']:.2f}%")
        print(f"   Final status: {trade_details['trade']['status']}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_virtual_trades()