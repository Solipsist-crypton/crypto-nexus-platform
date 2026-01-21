#!/usr/bin/env python3
"""Тест імпортів ф'ючерсного модуля - запускати з кореня бекенду"""

import sys
import os

# Додаємо корінь проекту до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_root)

print(f"Python path: {sys.path[0]}")
print(f"Current dir: {current_dir}")
print()

def test_imports():
    """Тестуємо всі критичні імпорти"""
    tests = [
        ("from app.futures.models import Signal", "Signal модель"),
        ("from app.futures.models import VirtualTrade", "VirtualTrade модель"),
        ("from app.futures.services.explanation_builder import ExplanationBuilder", "ExplanationBuilder"),
        ("from app.futures.api.router import router", "Router"),
    ]
    
    print("=== Testing Futures Module Imports ===\n")
    
    all_passed = True
    for import_stmt, name in tests:
        try:
            exec(import_stmt, globals())
            print(f"✅ {name}: OK")
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    # Тестуємо Celery завдання
    print("\n=== Testing Celery Task Imports ===")
    try:
        from app.futures.tasks.monitor_trades import celery_app
        print("✅ Celery app: OK")
    except Exception as e:
        print(f"❌ Celery app: FAILED - {e}")
        all_passed = False
    
    # Тестуємо ExplanationBuilder функціонал
    print("\n=== Testing ExplanationBuilder ===")
    try:
        from app.futures.services.explanation_builder import explanation_builder
        explanation = explanation_builder.build_explanation(
            symbol="BTCUSDT",
            direction="long",
            confidence=0.75
        )
        print(f"✅ ExplanationBuilder: OK")
        print(f"   Generated: {explanation[:80]}...")
    except Exception as e:
        print(f"❌ ExplanationBuilder: FAILED - {e}")
        all_passed = False
    
    print(f"\n=== {'All tests PASSED' if all_passed else 'Some tests FAILED'} ===")
    return all_passed

if __name__ == "__main__":
    test_imports()