# backend/test_professional_signals.py
import sys
sys.path.append('.')
from app.futures.services.ai_analyzer import AIAnalyzer
import json
from datetime import datetime

def test_professional_signals():
    print("🎯 ТЕСТ ПРОФЕСІЙНИХ AI СИГНАЛІВ (ПОВНИЙ НАБІР)")
    print("=" * 70)
    
    analyzer = AIAnalyzer()
    
    # ТОП монети для максимального прибутку
    symbols = [
        'BTC/USDT:USDT',
        'ETH/USDT:USDT', 
        'SOL/USDT:USDT',
        'XRP/USDT:USDT',
        'ADA/USDT:USDT',
        'AVAX/USDT:USDT',
        'DOT/USDT:USDT',
        'DOGE/USDT:USDT'
    ]
    
    all_signals = []
    
    for symbol in symbols:
        print(f"\n🔍 {symbol}:")
        print("-" * 40)
        
        try:
            signal = analyzer.analyze_market(symbol, '1h')
            
            if signal['direction'] != 'neutral':
                print(f"   🚀 СИГНАЛ: {signal['direction'].upper()} ({signal['confidence']*100}%)")
                print(f"   💰 Вхід: ${signal['entry_price']}")
                print(f"   📈 TP: ${signal['take_profit']} (+{((signal['take_profit']-signal['entry_price'])/signal['entry_price']*100):.2f}%)")
                print(f"   📉 SL: ${signal['stop_loss']} (-{((signal['entry_price']-signal['stop_loss'])/signal['entry_price']*100):.2f}%)")
                print(f"   ⚖️  Risk/Reward: 1:{signal['risk_reward']:.2f}")
                print(f"   📊 Очікуваний PnL: {signal['expected_pnl_percent']}%")
                print(f"   📏 Розмір позиції: {signal['position_size']['size_percent']}%")
                print(f"   💪 Сила: {signal['signal_strength']}")
                
                # Додаткові індикатори
                print(f"\n   📋 ІНДИКАТОРИ:")
                ind = signal.get('indicators_summary', {})
                print(f"      RSI/Stoch: {ind.get('rsi', 'N/A')}/{ind.get('stoch_rsi', 'N/A')}")
                print(f"      MACD: {ind.get('macd_hist', 'N/A')}")
                print(f"      VWAP: ціна {ind.get('vwap_position', 'N/A')}")
                print(f"      Ichimoku: {ind.get('ichimoku_cloud', 'N/A')}")
                print(f"      Williams %R: {ind.get('williams_r', 'N/A')}")
                
                all_signals.append(signal)
            else:
                print(f"   ⚪ NEUTRAL ({signal['confidence']*100}%) - чекаємо")
                print(f"   💰 Ціна: ${signal['entry_price']}")
                
        except Exception as e:
            print(f"   ❌ ПОМИЛКА: {str(e)[:50]}")
    
    # Статистика
    print(f"\n📊 ЗАГАЛЬНА СТАТИСТИКА:")
    print(f"   📈 Сигналів: {len([s for s in all_signals if s['direction'] == 'long'])} LONG")
    print(f"   📉 Сигналів: {len([s for s in all_signals if s['direction'] == 'short'])} SHORT")
    print(f"   ⚪ Сигналів: {len([s for s in all_signals if s['direction'] == 'neutral'])} NEUTRAL")
    
    # Збереження для аналізу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"professional_signals_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_signals, f, indent=2, default=str)
    
    print(f"\n💾 Сигнали збережено в {filename}")
    print(f"\n✅ ПРОФЕСІЙНИЙ ТЕСТ ЗАВЕРШЕНО!")
    
    return all_signals

if __name__ == "__main__":
    test_professional_signals()