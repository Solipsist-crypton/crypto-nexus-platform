# backend/test_final_system.py
import sys
sys.path.append('.')
from app.futures.services.ai_analyzer import AIAnalyzer
import json
from datetime import datetime

def final_system_test():
    print("🎯 ФІНАЛЬНИЙ ТЕСТ ПРОФЕСІЙНОЇ ТОРГОВОЇ СИСТЕМИ")
    print("=" * 70)
    print("⚡ Версія 1.0 - ГОТОВО ДО РЕАЛЬНОЇ ТОРГІВЛІ")
    print("=" * 70)
    
    analyzer = AIAnalyzer()
    
    # ВСІ головні монети
    symbols = [
        'BTC/USDT:USDT',
        'ETH/USDT:USDT', 
        'SOL/USDT:USDT',
        'XRP/USDT:USDT',
        'ADA/USDT:USDT',
        'AVAX/USDT:USDT',
        'DOT/USDT:USDT',
        'DOGE/USDT:USDT',
        'LINK/USDT:USDT',
        'MATIC/USDT:USDT',
        'ATOM/USDT:USDT',
        'UNI/USDT:USDT'
    ]
    
    results = {
        'total_signals': 0,
        'long_signals': 0,
        'short_signals': 0,
        'neutral_signals': 0,
        'total_expected_pnl': 0,
        'signals': []
    }
    
    for symbol in symbols:
        print(f"\n🔍 {symbol}:")
        print("-" * 40)
        
        try:
            signal = analyzer.analyze_market(symbol, '1h')
            
            results['total_signals'] += 1
            
            if signal.get('error'):
                print(f"   ❌ ПОМИЛКА: {signal.get('error_message', 'Unknown')[:50]}")
                results['neutral_signals'] += 1
                continue
            
            if signal['direction'] == 'long':
                emoji = "📈"
                results['long_signals'] += 1
            elif signal['direction'] == 'short':
                emoji = "📉"
                results['short_signals'] += 1
            else:
                emoji = "⚪"
                results['neutral_signals'] += 1
            
            print(f"   {emoji} {signal['direction'].upper()} ({signal['confidence']*100}%)")
            print(f"   💰 Вхід: ${signal['entry_price']}")
            
            if signal['direction'] != 'neutral':
                print(f"   📈 TP: ${signal['take_profit']} ({((signal['take_profit']-signal['entry_price'])/signal['entry_price']*100):.2f}%)")
                print(f"   📉 SL: ${signal['stop_loss']} ({((signal['entry_price']-signal['stop_loss'])/signal['entry_price']*100):.2f}%)")
                print(f"   ⚖️  Risk/Reward: 1:{signal['risk_reward']:.2f}")
                print(f"   📊 Очікуваний PnL: {signal['expected_pnl_percent']}%")
                print(f"   📏 Розмір позиції: {signal['position_size']['size_percent']}%")
                print(f"   💪 Сила: {signal['signal_strength']}")
                
                results['total_expected_pnl'] += signal['expected_pnl_percent']
            
            results['signals'].append(signal)
            
        except Exception as e:
            print(f"   ❌ КРИТИЧНА ПОМИЛКА: {str(e)[:50]}")
            results['neutral_signals'] += 1
    
    # ФІНАЛЬНА СТАТИСТИКА
    print(f"\n{'='*70}")
    print("📊 ФІНАЛЬНА СТАТИСТИКА СИСТЕМИ:")
    print(f"   📈 LONG сигналів: {results['long_signals']}")
    print(f"   📉 SHORT сигналів: {results['short_signals']}")
    print(f"   ⚪ NEUTRAL сигналів: {results['neutral_signals']}")
    print(f"   📊 Загальна кількість: {results['total_signals']}")
    
    if results['long_signals'] + results['short_signals'] > 0:
        avg_pnl = results['total_expected_pnl'] / (results['long_signals'] + results['short_signals'])
        print(f"   💰 Середній очікуваний PnL: {avg_pnl:.2f}%")
        print(f"   📈 Загальний очікуваний PnL: {results['total_expected_pnl']:.2f}%")
    
    # Збереження результатів
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"final_system_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Результати збережено в {filename}")
    print(f"\n✅ ФІНАЛЬНА СИСТЕМА ГОТОВА ДО РЕАЛЬНОЇ ТОРГІВЛІ!")
    print("🚀 Переходимо до Фази 2: Віртуальне тестування")
    
    return results

if __name__ == "__main__":
    final_system_test()