# backend/tests/test_ai_learning_full.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.futures.models.ai_learning_analyzer import AILearningAnalyzer

def create_realistic_crypto_data(symbol='BTC/USDT', num_candles=200):
    """Створення реалістичних крипто-даних для тестування"""
    dates = pd.date_range(start='2024-01-01', periods=num_candles, freq='H')
    
    # Детермінована цінова дія
    t = np.arange(num_candles)
    
    # 1. Базовий тренд
    trend = np.linspace(0, 15, num_candles)
    
    # 2. Осциляції
    oscillation = 8 * np.sin(2 * np.pi * t / 30)
    
    # 3. Короткострокові сплески
    spikes = np.zeros(num_candles)
    spike_indices = [30, 90, 150]
    for idx in spike_indices:
        if idx < num_candles:
            spikes[idx:idx+10] = 12 * np.sin(np.pi * np.arange(10) / 10)
    
    # Збираємо ціну
    base_price = 45000
    close = base_price + trend + oscillation + spikes
    
    # High/Low логіка
    high = close + 150 + 50 * np.sin(2 * np.pi * t / 25)
    low = close - 150 - 50 * np.cos(2 * np.pi * t / 25)
    
    # Open = попередній close з small noise
    open_price = np.roll(close, 1)
    open_price[0] = close[0] - 50
    
    # Обсяги зі сплесками на рухах
    volume_base = 1000
    volume = volume_base + 800 * np.abs(np.sin(2 * np.pi * t / 35))
    
    # Сплески обсягів на spike_indices
    for idx in spike_indices:
        if idx < num_candles:
            volume[idx:idx+8] = 3500
    
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    return df

def test_learning_analyzer_full():
    """Повний тест нового AI аналізатора з навчанням"""
    print("🧪 ТЕСТУВАННЯ AI АНАЛІЗАТОРА З МЕХАНІЗМОМ НАВЧАННЯ")
    print("=" * 70)
    
    # ===== 1. ІНІЦІАЛІЗАЦІЯ =====
    print("\n1. 🏁 ІНІЦІАЛІЗАЦІЯ АНАЛІЗАТОРА")
    analyzer = AILearningAnalyzer()
    
    initial_report = analyzer.get_learning_report()
    print(f"   • Режим: {'НАВЧАННЯ' if initial_report['learning_mode'] else 'ТОРГІВЛЯ'}")
    print(f"   • Прогрес: {initial_report['training_progress']}%")
    print(f"   • Загалом сигналів: {initial_report['total_signals']}")
    print(f"   • Поточна точність: {initial_report['current_accuracy']:.1%}")
    print(f"   • Днів навчання: {initial_report['days_learning']}")
    
    # ===== 2. СТВОРЕННЯ ТЕСТОВИХ ДАНИХ =====
    print("\n2. 📊 СТВОРЕННЯ ТЕСТОВИХ ДАНИХ")
    
    symbols_to_test = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    timeframes_to_test = ['1h', '4h']
    
    all_test_cases = []
    for symbol in symbols_to_test:
        for timeframe in timeframes_to_test:
            # Створюємо унікальні дані для кожного символу
            df = create_realistic_crypto_data(symbol, 200)
            all_test_cases.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'data': df
            })
    
    print(f"   • Створено {len(all_test_cases)} тестових наборів")
    print(f"   • Символи: {', '.join(symbols_to_test)}")
    print(f"   • Таймфрейми: {', '.join(timeframes_to_test)}")
    
    # ===== 3. ТЕСТ ГЕНЕРАЦІЇ СИГНАЛІВ =====
    print("\n3. 📈 ТЕСТ ГЕНЕРАЦІЇ СИГНАЛІВ")
    
    generated_signals = []
    
    for i, test_case in enumerate(all_test_cases, 1):
        print(f"   [{i}/{len(all_test_cases)}] Тест {test_case['symbol']} на {test_case['timeframe']}...")
        
        # Генеруємо сигнал з навчанням
        signal = analyzer.generate_trading_signal_with_learning(
            test_case['symbol'],
            test_case['data'],
            test_case['timeframe']
        )
        
        generated_signals.append(signal)
        
        print(f"     → {signal['direction'].upper()} | Confidence: {signal['confidence']:.1%} | "
              f"Quality: {signal['learning_data']['signal_quality']:.1%}")
    
    # ===== 4. ТЕСТ ОНОВЛЕННЯ РЕЗУЛЬТАТІВ =====
    print("\n4. 📊 ТЕСТ ОНОВЛЕННЯ РЕЗУЛЬТАТІВ")
    
    for i, signal in enumerate(generated_signals, 1):
        if 'learning_signal_id' not in signal:
            continue
            
        print(f"   [{i}/{len(generated_signals)}] Оновлення результату для {signal['symbol']}...")
        
        # Детермінований результат на основі напрямку
        if signal['direction'] == 'long':
            # Для лонгів - 70% шанс виграшу
            result = 'win' if i % 10 < 7 else 'loss'
        elif signal['direction'] == 'short':
            # Для шортів - 65% шанс виграшу
            result = 'win' if i % 10 < 6.5 else 'loss'
        else:
            result = 'break_even'
        
        # Розраховуємо прибуток/збиток
        if result == 'win':
            profit_pct = np.random.uniform(1.5, 4.0)  # Прибуток 1.5-4%
        elif result == 'loss':
            profit_pct = -np.random.uniform(0.8, 2.0)  # Збиток 0.8-2%
        else:
            profit_pct = 0.0
        
        result_data = {
            'result': result,
            'profit_pct': profit_pct,
            'hold_time_hours': np.random.randint(2, 12),
            'max_drawdown': abs(profit_pct) * np.random.uniform(0.3, 0.6),
            'exit_timestamp': datetime.now().isoformat(),
            'exit_reason': 'target_hit' if result == 'win' else 'stop_loss'
        }
        
        analyzer.update_signal_result(signal['learning_signal_id'], result_data)
        
        result_emoji = '✅' if result == 'win' else '❌' if result == 'loss' else '⚖️'
        print(f"     → {result_emoji} {result.upper()} ({profit_pct:+.2f}%)")
    
    # ===== 5. ТЕСТ ОПТИМІЗАЦІЇ ТА ПРОГРЕСУ =====
    print("\n5. 🔧 ТЕСТ ОПТИМІЗАЦІЇ ТА ПРОГРЕСУ")
    
    # Отримуємо оновлений звіт
    updated_report = analyzer.get_learning_report()
    
    print(f"   • Загалом сигналів: {updated_report['total_signals']}")
    print(f"   • Перемог: {updated_report['winning_signals']}")
    print(f"   • Поразок: {updated_report['losing_signals']}")
    print(f"   • Точність: {updated_report['current_accuracy']:.1%}")
    print(f"   • Середній прибуток: +{updated_report['avg_profit_per_win']:.2f}%")
    print(f"   • Середній збиток: -{updated_report['avg_loss_per_loss']:.2f}%")
    print(f"   • Загальний прибуток: {updated_report['total_profit']:+.2f}%")
    print(f"   • Прогрес навчання: {updated_report['training_progress']}%")
    
    # Показуємо динамічні ваги
    print(f"   • Динамічні ваги:")
    for category, weight in updated_report['dynamic_weights'].items():
        print(f"     - {category}: {weight:.3f}")
    
    # Показуємо розмір бази знань
    kb_size = updated_report['knowledge_base_size']
    print(f"   • База знань:")
    print(f"     - Виграшні паттерни: {kb_size['winning_patterns']}")
    print(f"     - Програшні паттерни: {kb_size['losing_patterns']}")
    print(f"     - Статистика індикаторів: {kb_size['indicator_performance']}")
    
    # ===== 6. ТЕСТ РЕАЛЬНОЇ ТОРГІВЛІ =====
    print("\n6. 🚀 ТЕСТ АКТИВАЦІЇ РЕАЛЬНОЇ ТОРГІВЛІ")
    
    # Спроба активувати реальну торгівлю
    activation_result = analyzer.enable_real_trading(min_accuracy=0.55, min_signals=50)
    
    if activation_result['success']:
        print(f"   ✅ {activation_result['message']}")
        print(f"   • Точність: {activation_result['stats']['accuracy']:.1%}")
        print(f"   • Середній прибуток: +{activation_result['stats']['avg_profit']:.2f}%")
    else:
        print(f"   ⚠️ {activation_result['message']}")
        if 'required' in activation_result:
            print(f"   • Потрібно сигналів: {activation_result['required']}")
            print(f"   • Маємо сигналів: {activation_result['current']}")
        if 'accuracy' in activation_result:
            print(f"   • Поточна точність: {activation_result['accuracy']:.1%}")
            print(f"   • Потрібна точність: {activation_result['required_accuracy']:.1%}")
    
    # ===== 7. ТЕСТ ЗБЕРЕЖЕННЯ/ЗАВАНТАЖЕННЯ =====
    print("\n7. 💾 ТЕСТ ЗБЕРЕЖЕННЯ ТА ЗАВАНТАЖЕННЯ")
    
    # Зберігаємо базу знань
    analyzer._save_knowledge_base('test_knowledge_base.pkl')
    
    # Створюємо новий аналізатор і завантажуємо базу
    print("   Створюю новий аналізатор і завантажую базу знань...")
    new_analyzer = AILearningAnalyzer(config_file='test_knowledge_base.pkl')
    
    new_report = new_analyzer.get_learning_report()
    print(f"   ✅ База знань завантажена успішно!")
    print(f"   • Сигналів: {new_report['total_signals']}")
    print(f"   • Точність: {new_report['current_accuracy']:.1%}")
    print(f"   • Прогрес: {new_report['training_progress']}%")
    
    # ===== 8. ГЕНЕРАЦІЯ НОВОГО СИГНАЛУ З НАВЧАНИМ АНАЛІЗАТОРОМ =====
    print("\n8. 🎯 ГЕНЕРАЦІЯ СИГНАЛУ З НАВЧАНИМ АНАЛІЗАТОРОМ")
    
    # Створюємо нові дані для тесту
    test_df = create_realistic_crypto_data('BTC/USDT', 200)
    
    # Генеруємо сигнал з навченим аналізатором
    learned_signal = new_analyzer.generate_trading_signal_with_learning(
        'BTC/USDT',
        test_df,
        '1h'
    )
    
    print(f"   • Символ: {learned_signal['symbol']}")
    print(f"   • Напрямок: {learned_signal['direction'].upper()}")
    print(f"   • Впевненість: {learned_signal['confidence']:.1%}")
    print(f"   • Якість сигналу: {learned_signal['learning_data']['signal_quality']:.1%}")
    print(f"   • Дані навчання:")
    print(f"     - Режим: {'Навчання' if learned_signal['learning_data']['training_mode'] else 'Торгівля'}")
    print(f"     - Прогрес: {learned_signal['learning_data']['learning_progress']}%")
    
    if learned_signal['learning_data']['historical_performance']:
        hist = learned_signal['learning_data']['historical_performance']
        print(f"     - Схожих паттернів: {hist['similar_patterns_found']}")
        print(f"     - Історичний шанс: {hist['win_rate']:.1%}")
        print(f"     - Рекомендація: {hist['recommendation']}")
    
    # ===== 9. ФІНАЛЬНИЙ ЗВІТ =====
    print("\n" + "=" * 70)
    print("📋 ФІНАЛЬНИЙ ЗВІТ ПРО ТЕСТУВАННЯ")
    print("=" * 70)
    
    final_report = new_analyzer.get_learning_report()
    
    # Оцінка результату
    accuracy = final_report['current_accuracy']
    if accuracy > 0.65:
        rating = "ВІДМІННО 🎯"
    elif accuracy > 0.55:
        rating = "ДОБРЕ 👍"
    elif accuracy > 0.45:
        rating = "ЗАДОВІЛЬНО ✅"
    else:
        rating = "ПОТРЕБУЄ ПОКРАЩЕННЯ ⚠️"
    
    print(f"\n🏆 ОЦІНКА СИСТЕМИ: {rating}")
    print(f"   • Загальна точність: {accuracy:.1%}")
    print(f"   • Сигналів зібрано: {final_report['total_signals']}")
    print(f"   • Днів навчання: {final_report['days_learning']}")
    print(f"   • База знань: {final_report['knowledge_base_size']['winning_patterns'] + final_report['knowledge_base_size']['losing_patterns']} паттернів")
    
    # Статистика ефективності
    if final_report['winning_signals'] > 0 and final_report['losing_signals'] > 0:
        win_loss_ratio = final_report['winning_signals'] / final_report['losing_signals']
        profit_factor = (final_report['avg_profit_per_win'] * final_report['winning_signals']) / \
                       (final_report['avg_loss_per_loss'] * final_report['losing_signals']) \
                       if final_report['avg_loss_per_loss'] > 0 else 999
        
        print(f"\n📊 СТАТИСТИКА ЕФЕКТИВНОСТІ:")
        print(f"   • Win/Loss Ratio: {win_loss_ratio:.2f}")
        print(f"   • Profit Factor: {profit_factor:.2f}")
        print(f"   • Expectancy: {final_report['avg_profit_per_win'] * accuracy + final_report['avg_loss_per_loss'] * (1 - accuracy):.2f}%")
    
    # Рекомендації
    print(f"\n💡 РЕКОМЕНДАЦІЇ:")
    print(f"   1. {final_report['recommendation']}")
    
    if final_report['training_progress'] < 50:
        print(f"   2. Продовжуйте тестування щонайменше {int((50 - final_report['training_progress']) / 5)} днів")
    elif final_report['training_progress'] < 80:
        print(f"   2. Можете тестувати на реальних, але малих сумах")
    else:
        print(f"   2. Готово до повноцінної торгівлі")
    
    # Перевірка готовності до реальної торгівлі
    print(f"\n🚀 ГОТОВНІСТЬ ДО РЕАЛЬНОЇ ТОРГІВЛІ:")
    
    readiness_check = []
    
    # Критерій 1: Кількість сигналів
    if final_report['total_signals'] >= 100:
        readiness_check.append(("✅ Достатньо сигналів", f"{final_report['total_signals']}/100"))
    else:
        readiness_check.append(("❌ Недостатньо сигналів", f"{final_report['total_signals']}/100"))
    
    # Критерій 2: Точність
    if accuracy >= 0.6:
        readiness_check.append(("✅ Достатня точність", f"{accuracy:.1%}"))
    elif accuracy >= 0.55:
        readiness_check.append(("⚠️ Прийнятна точність", f"{accuracy:.1%}"))
    else:
        readiness_check.append(("❌ Низька точність", f"{accuracy:.1%}"))
    
    # Критерій 3: Прогрес навчання
    if final_report['training_progress'] >= 70:
        readiness_check.append(("✅ Високий прогрес", f"{final_report['training_progress']}%"))
    elif final_report['training_progress'] >= 50:
        readiness_check.append(("⚠️ Середній прогрес", f"{final_report['training_progress']}%"))
    else:
        readiness_check.append(("❌ Низький прогрес", f"{final_report['training_progress']}%"))
    
    for check, value in readiness_check:
        print(f"   • {check}: {value}")
    
    # Загальний висновок
    ready_count = sum(1 for check, _ in readiness_check if check.startswith("✅"))
    warning_count = sum(1 for check, _ in readiness_check if check.startswith("⚠️"))
    
    print(f"\n📈 ЗАГАЛЬНИЙ ВИСНОВОК:")
    if ready_count == 3:
        print(f"   🎉 СИСТЕМА ГОТОВА ДО РЕАЛЬНОЇ ТОРГІВЛІ!")
    elif ready_count >= 2 or (ready_count == 1 and warning_count == 2):
        print(f"   ⚡ СИСТЕМА МАЙЖЕ ГОТОВА - можна тестувати з обережністю")
    else:
        print(f"   🔄 ПРОДОВЖУЙТЕ НАВЧАННЯ - система потребує більше даних")
    
    return new_analyzer, learned_signal, final_report

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 ЗАПУСК ПОВНОГО ТЕСТУ AI АНАЛІЗАТОРА З НАВЧАННЯМ")
    print("=" * 70)
    
    try:
        analyzer, last_signal, report = test_learning_analyzer_full()
        
        # Додатковий тест для перевірки збереження
        print(f"\n💾 Тестую збереження бази знань у файл...")
        analyzer._save_knowledge_base('final_knowledge_base.pkl')
        print(f"✅ База знань збережена у 'final_knowledge_base.pkl'")
        
        # Перевірка розміру файлу
        if os.path.exists('final_knowledge_base.pkl'):
            file_size = os.path.getsize('final_knowledge_base.pkl') / 1024
            print(f"📁 Розмір файлу: {file_size:.1f} KB")
        
        print(f"\n🎯 ТЕСТУВАННЯ УСПІШНО ЗАВЕРШЕНО!")
        print(f"   • Створено: AILearningAnalyzer з механізмом навчання")
        print(f"   • Протестовано: {report['total_signals']} сигналів")
        print(f"   • Точність: {report['current_accuracy']:.1%}")
        print(f"   • База знань: збережена у файл")
        
    except Exception as e:
        print(f"\n❌ ПОМИЛКА ПІД ЧАС ТЕСТУВАННЯ:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()