import requests

BASE_URL = "http://localhost:5000/api/futures"

# Тестуємо всі ендпоінти
endpoints = [
    "/health",
    "/test", 
    "/explain",
    "/explain?symbol=ETHUSDT&direction=short&confidence=0.82",
    "/signals/generate"
]

for endpoint in endpoints:
    print(f"\n{'='*50}")
    print(f"Testing: {endpoint}")
    print('='*50)
    
    if endpoint == "/signals/generate":
        response = requests.post(BASE_URL + endpoint)
    else:
        response = requests.get(BASE_URL + endpoint)
    
    if response.status_code == 200:
        print("✅ Success")
        print(response.json())
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)