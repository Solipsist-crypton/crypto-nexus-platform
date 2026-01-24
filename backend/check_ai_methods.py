import sys
sys.path.append('.')
from app.futures.services.ai_analyzer import AIAnalyzer

# Перевіряємо які методи є
analyzer = AIAnalyzer()
methods = [m for m in dir(analyzer) if not m.startswith('__')]
print("📋 Методи AIAnalyzer:")
for method in methods:
    print(f"  - {method}")

# Шукаємо методи з "indicator"
indicator_methods = [m for m in methods if 'indicator' in m.lower()]
print("\n🎯 Методи з 'indicator':", indicator_methods)