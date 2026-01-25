# backend/test_docker_fix.py
import requests
import time

print("🧪 ТЕСТ ПОСЛЯ DOCKER ФІКСУ")
print("=" * 50)

# Чекаємо поки сервер запуститься
time.sleep(3)

endpoints = [
    "http://localhost:5000/api/futures/signals",
    "http://localhost:5000/api/futures/health",
    "http://localhost:5000/api/futures/virtual-trades",
    "http://localhost:5000/api/futures/entry-points/active",
]

for endpoint in endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        print(f"\n🔍 {endpoint}")
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'signals' in data:
                print(f"   📋 Signals: {len(data['signals'])}")
                if data['signals']:
                    print(f"   🎯 Перший: {data['signals'][0]['symbol']}")
            elif 'count' in data:
                print(f"   📊 Count: {data['count']}")
    except Exception as e:
        print(f"❌ Помилка {endpoint}: {e}")

print("\n✅ ТЕСТ ЗАВЕРШЕНО")