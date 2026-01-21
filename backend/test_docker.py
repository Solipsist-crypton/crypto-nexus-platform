#!/usr/bin/env python3
"""Тест через Docker API"""

import requests
import json

BASE_URL = "http://localhost:5000/api/futures"

def test_with_docker():
    print("=== Тестування через Docker API ===\n")
    
    # 1. Health check
    print("1. Health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   {response.json()}")
    
    # 2. Generate a signal via API
    print("\n2. Generating signal via API...")
    response = requests.post(f"{BASE_URL}/signals/generate")
    if response.status_code == 200:
        signal = response.json()['signal']
        print(f"   Generated: {signal['symbol']} {signal['direction']}")
        print(f"   Entry: ${signal['entry_price']}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # 3. Create virtual trade (use signal_id=1 as fallback)
    print("\n3. Creating virtual trade...")
    params = {
        "signal_id": 1,
        "entry_price": 42200.0,
        "take_profit": 44500.0,
        "stop_loss": 41800.0
    }
    
    response = requests.post(f"{BASE_URL}/virtual-trades", params=params)
    
    if response.status_code == 200:
        trade = response.json()['trade']
        trade_id = trade['id']
        print(f"   ✅ Trade created: ID {trade_id}")
        print(f"   Status: {trade['status']}, PnL: {trade['pnl_percentage']}%")
        
        # 4. Test price update
        print(f"\n4. Testing price update for trade {trade_id}...")
        
        test_prices = [42300, 42500, 42800, 43200]
        
        for price in test_prices:
            update_response = requests.post(
                f"{BASE_URL}/virtual-trades/{trade_id}/update-price",
                params={"current_price": price}
            )
            
            if update_response.status_code == 200:
                updated = update_response.json()['trade']
                print(f"   Price ${price}: PnL {updated['pnl_percentage']}%, Status: {updated['status']}")
            else:
                print(f"   ❌ Update failed: {update_response.text}")
        
    else:
        print(f"   ❌ Failed to create trade: {response.text}")
        
        # Try without signal_id
        print("\n   Trying without signal_id...")
        params = {
            "entry_price": 42200.0,
            "take_profit": 44500.0,
            "stop_loss": 41800.0
        }
        
        response = requests.post(f"{BASE_URL}/virtual-trades", params=params)
        if response.status_code == 200:
            print(f"   ✅ Trade created without signal_id")
            print(f"   {response.json()}")
    
    # 5. List all trades
    print("\n5. Listing all virtual trades...")
    response = requests.get(f"{BASE_URL}/virtual-trades")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {data['count']} trades")
        for trade in data['trades']:
            print(f"   - ID {trade['id']}: {trade['status']}, PnL: {trade['pnl_percentage']}%")

if __name__ == "__main__":
    test_with_docker()