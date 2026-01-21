#!/usr/bin/env python3
"""Тестування віртуальних угод"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/futures"

def test_virtual_trading():
    print("=== Тестування віртуальних угод ===\n")
    
    # 1. Отримуємо або створюємо сигнал
    print("1. Отримуємо список сигналів...")
    # Спочатку створимо сигнал через API
    response = requests.post(f"{BASE_URL}/signals/generate")
    
    if response.status_code != 200:
        print("❌ Не вдалося створити тестовий сигнал")
        return
    
    signal_data = response.json()['signal']
    print(f"   ✅ Сигнал створено: {signal_data['symbol']} {signal_data['direction']}")
    print(f"   Entry: ${signal_data['entry_price']}, TP: ${signal_data['take_profit']}, SL: ${signal_data['stop_loss']}")
    
    # Для реального тесту потрібен signal_id з БД
    # Тимчасово використаємо ID=1 (якщо створили через create_test_data.py)
    signal_id = 1
    
    # 2. Створюємо віртуальну угоду
    print(f"\n2. Створюємо віртуальну угоду для сигналу ID={signal_id}...")
    
    entry_price = signal_data['entry_price']
    take_profit = signal_data['take_profit']
    stop_loss = signal_data['stop_loss']
    
    response = requests.post(
        f"{BASE_URL}/virtual-trades",
        params={
            "signal_id": signal_id,
            "entry_price": entry_price,
            "take_profit": take_profit,
            "stop_loss": stop_loss
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Помилка створення угоди: {response.status_code}")
        print(response.text)
        # Спробуємо без signal_id
        response = requests.post(
            f"{BASE_URL}/virtual-trades",
            params={
                "signal_id": 1,  # Спробуємо з ID=1
                "entry_price": 42150.0,
                "take_profit": 44000.0,
                "stop_loss": 41500.0
            }
        )
    
    if response.status_code == 200:
        trade_data = response.json()
        trade_id = trade_data['trade']['id']
        print(f"   ✅ Віртуальна угода створена: ID {trade_id}")
        print(f"   Статус: {trade_data['trade']['status']}")
        print(f"   PnL: {trade_data['trade']['pnl_percentage']}%")
    else:
        print(f"❌ Не вдалося створити угоду: {response.text}")
        return
    
    # 3. Тестуємо оновлення ціни
    print(f"\n3. Тестуємо оновлення ціни для угоди ID={trade_id}...")
    
    # Симулюємо різні ціни
    test_scenarios = [
        ("Малий зріст", entry_price * 1.005),   # +0.5%
        ("Помірний зріст", entry_price * 1.015), # +1.5%
        ("Сильний зріст", entry_price * 1.03),   # +3.0%
        ("Досягнення TP", take_profit * 1.001),  # Трохи вище TP
    ]
    
    for scenario_name, price in test_scenarios:
        print(f"   {scenario_name}: ${price:.2f}")
        
        response = requests.post(
            f"{BASE_URL}/virtual-trades/{trade_id}/update-price",
            params={"current_price": price}
        )
        
        if response.status_code == 200:
            update_data = response.json()
            status = update_data['trade']['status']
            pnl = update_data['trade']['pnl_percentage']
            
            print(f"     PnL: {pnl}%, Статус: {status}")
            
            if status != 'active':
                print(f"     🎯 Угода завершена: {status}")
                break
        else:
            print(f"     ❌ Помилка: {response.text}")
        
        time.sleep(0.5)  # Невелика пауза
    
    # 4. Отримуємо деталі угоди
    print(f"\n4. Отримуємо деталі угоди ID={trade_id}...")
    response = requests.get(f"{BASE_URL}/virtual-trades/{trade_id}")
    
    if response.status_code == 200:
        trade_details = response.json()
        print(f"   Фінальний статус: {trade_details['trade']['status']}")
        print(f"   Фінальний PnL: {trade_details['trade']['pnl_percentage']}%")
        print(f"   Створено: {trade_details['trade']['created_at']}")
    
    # 5. Отримуємо всі угоди
    print(f"\n5. Список всіх віртуальних угод...")
    response = requests.get(f"{BASE_URL}/virtual-trades")
    
    if response.status_code == 200:
        all_trades = response.json()
        print(f"   Знайдено угод: {all_trades['count']}")
        
        for trade in all_trades['trades'][:3]:  # Перші 3
            print(f"   - ID {trade['id']}: {trade['status']}, PnL: {trade['pnl_percentage']}%")
    
    print("\n=== Тестування завершено ===")

if __name__ == "__main__":
    test_virtual_trading()