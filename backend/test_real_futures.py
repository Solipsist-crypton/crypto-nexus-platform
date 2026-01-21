# backend/test_real_futures.py
import asyncio
from app.futures.models.exchange_connector import ExchangeConnector
from app.futures.models.ai_analyzer import AIAnalyzer
from app.futures.models.risk_manager import RiskManager
from app.futures.services.signal_orchestrator import SignalOrchestrator
import pandas as pd

class RealFuturesTester:
    def __init__(self):
        self.exchange = ExchangeConnector('binance')
        self.analyzer = AIAnalyzer()
        self.risk_manager = RiskManager()
        
    def test_real_data(self):
        """Тест з реальними даними з Binance"""
        symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
        
        for symbol in symbols:
            print(f"\n🔍 Аналіз {symbol}")
            print("=" * 50)
            
            try:
                # Отримання реальних даних
                df = self.exchange.fetch_ohlcv(symbol, '1h', 200)
                
                if len(df) < 50:
                    print(f"Недостатньо даних для {symbol}")
                    continue
                
                # Розрахунок індикаторів
                indicators = self.analyzer.calculate_indicators(df)
                
                # Генерація сигналу
                signal = self.analyzer.generate_signal(symbol, df, indicators)
                
                # Аналіз структури ринку
                structure = self.analyzer.analyze_market_structure(df)
                
                # Отримання фандинг рейту
                funding = self.exchange.fetch_funding_rate(symbol)
                
                print(f"📊 Ціна: ${signal['entry_price']}")
                print(f"📈 Напрямок: {signal['direction'].upper()}")
                print(f"🎯 Впевненість: {signal['confidence'] * 100}%")
                print(f"💰 TP: ${signal['take_profit']} | SL: ${signal['stop_loss']}")
                print(f"📐 Тренд: {structure['trend']}")
                print(f"🔄 RSI: {signal['indicators']['rsi']}")
                print(f"📊 MACD Hist: {signal['indicators']['macd_hist']}")
                if funding:
                    print(f"💸 Фандинг рейт: {funding['fundingRate'] * 100}%")
                
                # Перевірка ризиків
                portfolio_value = 10000  # Приклад
                sl_distance = abs(signal['entry_price'] - signal['stop_loss']) / signal['entry_price']
                position_size = self.risk_manager.calculate_position_size(
                    portfolio_value, signal['confidence'], sl_distance
                )
                
                print(f"⚖️  Розмір позиції: ${position_size:.2f}")
                print(f"📉 Ризик: {sl_distance * 100:.2f}%")
                
            except Exception as e:
                print(f"❌ Помилка при аналізі {symbol}: {str(e)}")
    
    async def live_test(self):
        """Тест в реальному часі"""
        print("\n🎯 ТЕСТ В РЕАЛЬНОМУ ЧАСІ")
        print("=" * 50)
        
        orchestrator = SignalOrchestrator()
        
        while True:
            signals = await orchestrator.generate_live_signals()
            
            for signal in signals:
                if signal['confidence'] > 0.7:  # Тільки високої впевненості
                    print(f"\n🚀 СИГНАЛ: {signal['symbol']}")
                    print(f"   Напрямок: {signal['direction']}")
                    print(f"   Впевненість: {signal['confidence']}")
                    print(f"   Час: {signal['timestamp']}")
                    
            await asyncio.sleep(300)  # Очікування 5 хвилин

if __name__ == "__main__":
    tester = RealFuturesTester()
    
    print("🧪 ТЕСТ РЕАЛЬНИХ ДАНИХ З BINANCE FUTURES")
    print("=" * 60)
    
    # Тест з історичними даними
    tester.test_real_data()
    
    # Запуск тесту в реальному часі (за бажанням)
    # asyncio.run(tester.live_test())