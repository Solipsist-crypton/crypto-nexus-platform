# backend/test_entry_points_fixed.py
import requests

BASE_URL = "http://localhost:5000/api/futures"  # Без /v1!

print("🧪 ТЕСТ СИСТЕМИ ТОЧОК ВХОДУ (ФІКСОВАНИЙ)")
print("=" * 60)

def test_fixed():
    try:
        # 1. Отримати сигнали (перевірити чи API працює)
        print("1. 📊 Отримуємо сигнали...")
        response = requests.get(f"{BASE_URL}/signals")
        
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            print(f"   ✅ Знайдено {len(signals)} сигналів")
            
            if signals:
                signal_id = signals[0]['id']
                print(f"\n2. 🎯 Перевіряємо віртуальні угоди...")
                
                # Перевірити чи є вже угоди
                trades_response = requests.get(f"{BASE_URL}/virtual-trades")
                if trades_response.status_code == 200:
                    trades_data = trades_response.json()
                    print(f"   📈 Віртуальних угод: {trades_data.get('count', 0)}")
                
                # Тестуємо створення нової угоди
                print(f"\n3. 🚀 Створюємо нову віртуальну угоду...")
                create_response = requests.post(f"{BASE_URL}/virtual-trades/{signal_id}")
                
                if create_response.status_code == 200:
                    create_data = create_response.json()
                    print(f"   ✅ Створено угоду #{create_data.get('trade', {}).get('id', 'N/A')}")
                    
                    # Перевірити статистику
                    print(f"\n4. 📊 Отримуємо статистику...")
                    stats_response = requests.get(f"{BASE_URL}/virtual-trades/statistics")
                    if stats_response.status_code == 200:
                        stats = stats_response.json()
                        print(f"   🎯 Win Rate: {stats.get('win_rate', 0)}%")
                        print(f"   💰 Total PnL: {stats.get('total_pnl', 0)}%")
                else:
                    print(f"   ❌ Помилка створення: {create_response.text}")
            else:
                print("   ℹ️ Немає сигналів для тесту")
        else:
            print(f"   ❌ Помилка отримання сигналів: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущено")
        print("   Запустіть: uvicorn app.main:app --reload --port 5000")
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    test_fixed()
    print("\n✅ ТЕСТ ЗАВЕРШЕНО")