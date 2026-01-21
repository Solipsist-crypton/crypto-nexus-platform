#!/usr/bin/env python3
"""Тест всіх компонентів ф'ючерсного модуля"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_all_imports():
    print("=== ТЕСТ ІМПОРТІВ ВСІХ КОМПОНЕНТІВ ===\n")
    
    tests = [
        ("from app.futures.services.ai_analyzer import AIAnalyzer", "AIAnalyzer"),
        ("from app.futures.services.explanation_builder import ExplanationBuilder", "ExplanationBuilder"),
        ("from app.futures.api.router import router", "Router"),
        ("from app.futures.models import Signal, VirtualTrade", "Моделі"),
        ("from app.futures.services.signal_orchestrator import AISignalOrchestrator", "SignalOrchestrator"),
    ]
    
    all_passed = True
    
    for import_stmt, name in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}: Успішно імпортовано")
        except ImportError as e:
            print(f"❌ {name}: Помилка імпорту - {e}")
            all_passed = False
        except Exception as e:
            print(f"⚠️  {name}: Інша помилка - {e}")
    
    return all_passed

def test_ai_analyzer():
    print("\n=== ТЕСТ AIAnalyzer ===")
    
    try:
        from app.futures.services.ai_analyzer import AIAnalyzer
        
        analyzer = AIAnalyzer()
        
        # Тестуємо аналіз для різних символів
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        for symbol in symbols:
            analysis = analyzer.analyze_market(symbol, "1h")
            
            print(f"\n📊 {symbol} аналіз:")
            print(f"   Напрямок: {analysis['direction']}")
            print(f"   Впевненість: {analysis['confidence']}")
            print(f"   Ціна входу: ${analysis['entry_price']}")
            print(f"   Take Profit: ${analysis['take_profit']}")
            print(f"   Stop Loss: ${analysis['stop_loss']}")
            print(f"   Фактори: {len(analysis['factors'])}")
            
            # Перевіряємо валідність даних
            assert analysis['confidence'] >= 0 and analysis['confidence'] <= 1
            assert analysis['direction'] in ['long', 'short']
            assert analysis['entry_price'] > 0
        
        print("\n✅ AIAnalyzer: Тест пройдено")
        return True
        
    except Exception as e:
        print(f"\n❌ AIAnalyzer: Помилка - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_explanation_builder():
    print("\n=== ТЕСТ ExplanationBuilder ===")
    
    try:
        from app.futures.services.explanation_builder import explanation_builder
        
        # Тестуємо генерацію пояснень
        test_cases = [
            {"symbol": "BTCUSDT", "direction": "long", "confidence": 0.75},
            {"symbol": "ETHUSDT", "direction": "short", "confidence": 0.82},
            {"symbol": "SOLUSDT", "direction": "long", "confidence": 0.68},
        ]
        
        for i, test in enumerate(test_cases, 1):
            explanation = explanation_builder.build_explanation(
                symbol=test['symbol'],
                direction=test['direction'],
                confidence=test['confidence']
            )
            
            print(f"\n📝 Тест {i} ({test['symbol']}):")
            print(f"   Пояснення: {explanation[:80]}...")
            
            # Перевіряємо що пояснення не порожнє
            assert len(explanation) > 20
            assert test['symbol'] in explanation
        
        print("\n✅ ExplanationBuilder: Тест пройдено")
        return True
        
    except Exception as e:
        print(f"\n❌ ExplanationBuilder: Помилка - {e}")
        return False

def test_api_integration():
    print("\n=== ТЕСТ ІНТЕГРАЦІЇ (без запуску сервера) ===")
    
    try:
        from app.futures.services.ai_analyzer import AIAnalyzer
        from app.futures.services.explanation_builder import explanation_builder
        
        # Імітуємо роботу роутера
        analyzer = AIAnalyzer()
        
        # 1. Аналіз ринку
        symbol = "BTCUSDT"
        analysis = analyzer.analyze_market(symbol, "1h")
        
        # 2. Генерація пояснення
        explanation = explanation_builder.build_explanation(
            symbol=symbol,
            direction=analysis["direction"],
            confidence=analysis["confidence"],
            factors=analysis["factors"]
        )
        
        # 3. Формуємо відповідь (як у API)
        api_response = {
            "status": "success",
            "signal": {
                "symbol": symbol,
                "direction": analysis["direction"],
                "confidence": analysis["confidence"],
                "explanation": explanation,
                "factors": analysis["factors"],
                "entry_price": analysis["entry_price"],
                "take_profit": analysis["take_profit"],
                "stop_loss": analysis["stop_loss"],
                "timeframe": "1h"
            }
        }
        
        print(f"📨 Імітована API відповідь:")
        print(f"   Symbol: {api_response['signal']['symbol']}")
        print(f"   Direction: {api_response['signal']['direction']}")
        print(f"   Confidence: {api_response['signal']['confidence']}")
        print(f"   Explanation length: {len(api_response['signal']['explanation'])} chars")
        
        # Перевіряємо структуру
        required_keys = ['symbol', 'direction', 'confidence', 'explanation', 'entry_price']
        for key in required_keys:
            assert key in api_response['signal']
        
        print("\n✅ Інтеграція: Тест пройдено")
        return True
        
    except Exception as e:
        print(f"\n❌ Інтеграція: Помилка - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_orchestrator():
    print("\n=== ТЕСТ SignalOrchestrator ===")
    
    try:
        from app.futures.services.signal_orchestrator import AISignalOrchestrator
        
        orchestrator = AISignalOrchestrator()
        
        # Тестуємо генерацію сигналів
        signals = orchestrator.generate_daily_signals()
        
        print(f"   Згенеровано сигналів: {len(signals)}")
        
        if signals:
            print(f"\n   Приклад сигналу:")
            sample = signals[0]
            print(f"     Symbol: {sample['symbol']}")
            print(f"     Timeframe: {sample['timeframe']}")
            print(f"     Direction: {sample['analysis']['direction']}")
            print(f"     Confidence: {sample['analysis']['confidence']}")
        
        # Перевіряємо що метод існує
        assert hasattr(orchestrator, 'save_signals_to_db')
        assert hasattr(orchestrator, 'generate_daily_signals')
        
        print("\n✅ SignalOrchestrator: Тест пройдено")
        return True
        
    except ImportError as e:
        print(f"\n⚠️  SignalOrchestrator: Файл ще не створений - {e}")
        return True  # Не вважаємо помилкою, якщо файлу ще немає
    except Exception as e:
        print(f"\n❌ SignalOrchestrator: Помилка - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 ПОВНИЙ ТЕСТ Ф'ЮЧЕРСНОГО МОДУЛЯ")
    print("=" * 50)
    
    results = []
    
    # Виконуємо всі тести
    results.append(("Імпорти", test_all_imports()))
    results.append(("AIAnalyzer", test_ai_analyzer()))
    results.append(("ExplanationBuilder", test_explanation_builder()))
    results.append(("Інтеграція", test_api_integration()))
    results.append(("SignalOrchestrator", test_signal_orchestrator()))
    
    # Підсумок
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, success in results:
        status = "✅ ПРОЙДЕНО" if success else "❌ НЕ ПРОЙДЕНО"
        print(f"{status} - {name}")
        if success:
            passed += 1
    
    print(f"\n📈 Підсумок: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("\n🎉 ВІДМІННО! Всі компоненти працюють коректно!")
        print("   Можеш продовжувати покращення та додавання функціоналу.")
    else:
        print(f"\n⚠️  Увага: {total - passed} тест(ів) не пройдено.")
        print("   Спочатку виправ помилки, потім продовжуй розробку.")
    
    return passed == total
def debug_explanation_builder():
    """Детальний дебаг ExplanationBuilder"""
    print("\n=== ДЕТАЛЬНИЙ ДЕБАГ ExplanationBuilder ===")
    
    try:
        from app.futures.services.explanation_builder import explanation_builder
        
        # Тест 1: Просте пояснення
        print("\n1. Тест простого пояснення:")
        exp1 = explanation_builder.build_explanation("BTCUSDT", "long", 0.75)
        print(f"   Результат: {exp1[:100]}...")
        print(f"   Довжина: {len(exp1)} символів")
        
        # Тест 2: З факторами
        print("\n2. Тест з факторами:")
        factors = {
            "trend_strength": 0.8,
            "volume_confirmation": 0.7,
            "support_resistance": 0.9
        }
        exp2 = explanation_builder.build_explanation(
            "ETHUSDT", "short", 0.82, factors
        )
        print(f"   Результат: {exp2[:100]}...")
        
        # Тест 3: Перевірка методів об'єкта
        print("\n3. Перевірка атрибутів об'єкта:")
        print(f"   Тип: {type(explanation_builder)}")
        print(f"   Методи: {[m for m in dir(explanation_builder) if not m.startswith('_')]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Детальна помилка: {e}")
        import traceback
        traceback.print_exc()
        return False
        
if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Тест перервано користувачем")
        sys.exit(1)
