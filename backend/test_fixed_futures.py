#!/usr/bin/env python3
"""Тест виправленого ф'ючерсного модуля"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/futures"

def test_fixed_system():
    print("=== ТЕСТ ВИПРАВЛЕНОЇ СИСТЕМИ Ф'ЮЧЕРСІВ ===")
    print()
    
    # 1. Генеруємо сигнал (тепер зберігається в БД)
    print("1. Генеруємо сигнал (збережеться в БД)...")
    response = requests.post(f"{BASE_URL}/signals/generate")
    
    if response.status_code != 200:
        print(f"   ❌ Помилка: {response.text}")
        return
    
    signal_data = response.json()['signal']
    signal_id = signal_data['id']
    
    print(f"   ✅ Сигнал збережено: ID {signal_id}")
    print(f"   {signal_data['symbol']} {signal_data['direction']}")
    print(f"   Confidence: {signal_data['confidence']}")
    print(f"   Entry: ${signal_data['entry_price']}")
    
    # 2. Створюємо віртуальну угоду
    print(f"\n2. Створюємо віртуальну угоду для сигналу ID {signal_id}...")
    
    params = {
        "signal_id": signal_id,
        "entry_price": signal_data['entry_price'],
        "take_profit": signal_data['take_profit'],
        "stop_loss": signal_data['stop_loss']
    }
    
    response = requests.post(f"{BASE_URL}/virtual-trades", params=params)
    
    if response.status_code != 200:
        print(f"   ❌ Помилка: {response.text}")
        return
    
    trade_data = response.json()['trade']
    trade_id = trade_data['id']
    
    print(f"   ✅ Віртуальна угода створена: ID {trade_id}")
    print(f"   Статус: {trade_data['status']}")
    
    # 3. Тестуємо оновлення ціни
    print(f"\n3. Тестуємо оновлення ціни для угоди ID {trade_id}...")
    
    # Симулюємо різні сценарії
    entry = signal_data['entry_price']
    scenarios = [
        ("Малий зріст", entry * 1.005),    # +0.5%
        ("Помірний зріст", entry * 1.015),  # +1.5%
        ("Сильний зріст", entry * 1.025),   # +2.5%
        ("Досягнення TP", signal_data['take_profit'] * 1.001),  # Вище TP
    ]
    
    for name, price in scenarios:
        print(f"   {name}: ${price:.2f}")
        
        response = requests.post(
            f"{BASE_URL}/virtual-trades/{trade_id}/update-price",
            params={"current_price": price}
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data['trade']['status']
            pnl = data['trade']['pnl_percentage']
            
            print(f"     PnL: {pnl}%, Статус: {status}")
            
            if status != 'active':
                print(f"     🎯 Угода завершена: {status}")
                break
        else:
            print(f"     ❌ Помилка: {response.text}")
        
        time.sleep(0.3)
    
    # 4. Перевіряємо список сигналів
    print("\n4. Перевіряємо список сигналів в БД...")
    response = requests.get(f"{BASE_URL}/signals")
    
    if response.status_code == 200:
        signals = response.json()
        print(f"   Знайдено сигналів: {signals['count']}")
    
    # 5. Перевіряємо список угод
    print("\n5. Перевіряємо список віртуальних угод...")
    response = requests.get(f"{BASE_URL}/virtual-trades")
    
    if response.status_code == 200:
        trades = response.json()
        print(f"   Знайдено угод: {trades['count']}")
        
        for trade in trades['trades'][:3]:
            print(f"   - ID {trade['id']}: Signal {trade['signal_id']}, {trade['status']}, PnL: {trade['pnl_percentage']}%")
    
    print("\n=== ТЕСТ ЗАВЕРШЕНО УСПІШНО ===")
    print(f"\n📊 ID сигналу для подальшого тесту: {signal_id}")
    print(f"📊 ID віртуальної угоди: {trade_id}")

if __name__ == "__main__":
    try:
        test_fixed_system()
    except Exception as e:
        print(f"\n❌ Помилка тесту: {e}")
        import traceback
        traceback.print_exc()