# backend/test_api_structure.py
import requests

BASE_URL = "http://localhost:5000"

print("🔍 ПЕРЕВІРКА СТРУКТУРИ API")
print("=" * 60)

# Тестуємо всі можливі варіанти
test_endpoints = [
    # Поточний ваш prefix
    "/api/futures/signals",
    "/api/futures/virtual-trades",
    "/api/futures/entry-points/active",
    "/api/futures/entry-points",
    
    # Старий prefix
    "/api/v1/futures/signals",
    "/api/v1/futures/entry-points/active",
    
    # Без version
    "/api/futures/entry-points/active",
    
    # Кореневі
    "/",
    "/docs",
    "/redoc",
]

print("📡 Перевірка ендпоінтів:")
for endpoint in test_endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=3)
        if response.status_code < 400:
            print(f"✅ {endpoint:45} - {response.status_code}")
            if endpoint == "/api/futures/signals" and response.status_code == 200:
                data = response.json()
                print(f"   📊 Сигналів: {len(data.get('signals', []))}")
        elif response.status_code == 404:
            print(f"❌ {endpoint:45} - 404 (Not Found)")
        else:
            print(f"⚠️  {endpoint:45} - {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint:45} - Connection refused")
    except Exception as e:
        print(f"❌ {endpoint:45} - Error: {str(e)[:30]}")

# Тест POST запитів
print("\n🧪 Тест POST запитів:")
try:
    # Перевіримо чи можемо створити угоду
    response = requests.get(f"{BASE_URL}/api/futures/signals")
    if response.status_code == 200:
        signals = response.json().get('signals', [])
        if signals:
            signal_id = signals[0]['id']
            print(f"\n📊 Знайдено сигнал ID: {signal_id}")
            
            # Спробуємо створити віртуальну угоду
            print(f"🚀 Тест створення угоди для сигналу {signal_id}...")
            post_response = requests.post(f"{BASE_URL}/api/futures/virtual-trades/{signal_id}")
            print(f"   📤 POST статус: {post_response.status_code}")
            if post_response.status_code < 400:
                print(f"   📦 Відповідь: {post_response.json()}")
except Exception as e:
    print(f"❌ Помилка тесту: {e}")