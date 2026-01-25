# backend/test_real_signals.py
import sys
sys.path.append('.')
from app.futures.services.ai_analyzer import AIAnalyzer
import json

def test_real_analysis():
    print("🧪 ТЕСТ РЕАЛЬНИХ AI СИГНАЛІВ")
    print("=" * 60)
    
    analyzer = AIAnalyzer()
    
    symbols = [
    'BTC/USDT:USDT',
    'ETH/USDT:USDT', 
    'SOL/USDT:USDT',
    'XRP/USDT:USDT',      # Просто додайте сюди
    'ADA/USDT:USDT',
    'AVAX/USDT:USDT',
    'DOT/USDT:USDT',
    'DOGE/USDT:USDT',
    'LINK/USDT:USDT',
    'ATOM/USDT:USDT',
    'UNI/USDT:USDT',
    'FIL/USDT:USDT'
]
    
    for symbol in symbols:
        print(f"\n🔍 Аналіз {symbol}:")
        print("-" * 40)
        
        signal = analyzer.analyze_market(symbol, '1h')
        
        print(f"📊 Напрямок: {signal['direction'].upper()}")
        print(f"🎯 Впевненість: {signal['confidence'] * 100}%")
        print(f"💰 Вхід: ${signal['entry_price']}")
        print(f"📈 TP: ${signal['take_profit']}")
        print(f"📉 SL: ${signal['stop_loss']}")
        
        print(f"\n📋 Індикатори:")
        indicators = signal.get('indicators_summary', {})
        print(f"   RSI: {indicators.get('rsi', 'N/A')}")
        print(f"   MACD Hist: {indicators.get('macd_hist', 'N/A')}")
        print(f"   SMA 20/50: {indicators.get('sma_20', 'N/A')}/{indicators.get('sma_50', 'N/A')}")
        print(f"   ATR: {indicators.get('atr_percent', 'N/A')}%")
        print(f"   Volume Ratio: {indicators.get('volume_ratio', 'N/A')}")
        
        print(f"\n📝 Фактори:")
        for factor, value in signal.get('factors', {}).items():
            print(f"   {factor}: {value}")
    
    print(f"\n✅ Тест завершено!")
    return True

if __name__ == "__main__":
    test_real_analysis()