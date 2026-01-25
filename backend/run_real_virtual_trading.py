# backend/run_real_virtual_trading.py
import sys
import time
import schedule
from datetime import datetime
sys.path.append('.')
from app.database import SessionLocal
from app.futures.services.trade_executor import VirtualTradeExecutor
from app.futures.services.ai_analyzer import AIAnalyzer

def update_all_real_trades():
    """Оновлення всіх реальних AI угод"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n🕒 {timestamp} - Оновлення AI угод...")
    
    db = SessionLocal()
    try:
        executor = VirtualTradeExecutor()
        results = executor.update_all_active_trades(db)
        
        if results["total"] > 0:
            print(f"   📊 AI угод: {results['total']}")
            print(f"   🔄 Оновлено: {results['updated']}")
            
            if results["tp_hit"] > 0:
                print(f"   🎯 Take Profit: {results['tp_hit']}")
            if results["sl_hit"] > 0:
                print(f"   🛑 Stop Loss: {results['sl_hit']}")
            
            # Показуємо деталі угод
            if results["updated"] > 0:
                from app.futures.models import VirtualTrade
                active_trades = db.query(VirtualTrade).filter(
                    VirtualTrade.status == "active"
                ).limit(3).all()
                
                for trade in active_trades:
                    pnl_color = "🟢" if trade.pnl_percentage >= 0 else "🔴"
                    print(f"      {pnl_color} {trade.symbol}: {trade.pnl_percentage:.2f}%")
        else:
            print("   ℹ️ Немає активних AI угод")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    finally:
        db.close()

def generate_ai_signals_and_trades():
    """Генерація нових AI сигналів та створення угод"""
    print("\n🤖 ГЕНЕРАЦІЯ НОВИХ AI СИГНАЛІВ...")
    
    db = SessionLocal()
    try:
        analyzer = AIAnalyzer()
        executor = VirtualTradeExecutor()
        
        # Основні криптовалюты для аналізу
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
        
        created_signals = 0
        created_trades = 0
        
        for symbol in symbols[:3]:  # Тільки перші 3 для тесту
            print(f"\n🔍 Аналіз {symbol}...")
            
            try:
                # Генеруємо AI сигнал
                signal_data = analyzer.analyze_market(symbol, '1h')
                
                if signal_data.get('error'):
                    print(f"   ❌ Помилка: {signal_data.get('error_message', 'Unknown')[:30]}")
                    continue
                
                # Зберігаємо сигнал в БД
                from app.futures.models import Signal
                
                signal = Signal(
                    symbol=symbol,
                    direction=signal_data['direction'],
                    timeframe='1h',
                    entry_price=signal_data['entry_price'],
                    take_profit=signal_data['take_profit'],
                    stop_loss=signal_data['stop_loss'],
                    confidence=signal_data['confidence'],
                    reasoning_weights=signal_data.get('reasoning_weights', {}),
                    explanation_text=signal_data.get('explanation', ''),
                    is_active=True,
                    source='ai_v1'
                )
                
                db.add(signal)
                db.flush()  # Отримуємо ID
                
                created_signals += 1
                print(f"   ✅ AI сигнал: {signal.direction.upper()} ({signal.confidence*100:.0f}%)")
                print(f"      💰 Вхід: ${signal.entry_price:.2f}")
                print(f"      🎯 TP: ${signal.take_profit:.2f}")
                print(f"      🛑 SL: ${signal.stop_loss:.2f}")
                
                # Якщо сигнал впевнений (confidence > 70%), створюємо віртуальну угоду
                if signal.confidence >= 0.7:
                    trade = executor.create_virtual_trade(db, signal.id, user_id=1)
                    if trade:
                        created_trades += 1
                        print(f"      📝 Створено віртуальну угоду #{trade.id}")
                
            except Exception as e:
                print(f"   ❌ Помилка для {symbol}: {str(e)[:50]}")
                continue
        
        db.commit()
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"   🤖 Згенеровано сигналів: {created_signals}")
        print(f"   📝 Створено угод: {created_trades}")
        
    except Exception as e:
        print(f"❌ Критична помилка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def show_statistics():
    """Показ статистики віртуальної торгівлі"""
    db = SessionLocal()
    try:
        from app.futures.models import VirtualTrade
        
        all_trades = db.query(VirtualTrade).all()
        active_trades = [t for t in all_trades if t.status == "active"]
        closed_trades = [t for t in all_trades if t.status in ["tp_hit", "sl_hit"]]
        
        if closed_trades:
            winning_trades = [t for t in closed_trades if t.status == "tp_hit"]
            win_rate = (len(winning_trades) / len(closed_trades)) * 100
            total_pnl = sum(t.pnl_percentage for t in closed_trades)
        else:
            win_rate = 0
            total_pnl = 0
        
        print(f"\n📈 СТАТИСТИКА ВІРТУАЛЬНОЇ ТОРГІВЛІ:")
        print(f"   📊 Усього угод: {len(all_trades)}")
        print(f"   🔄 Активних: {len(active_trades)}")
        print(f"   ✅ Закритих: {len(closed_trades)}")
        print(f"   🎯 Переможних: {len([t for t in closed_trades if t.status == 'tp_hit'])}")
        print(f"   🛑 Програшних: {len([t for t in closed_trades if t.status == 'sl_hit'])}")
        print(f"   📈 Win Rate: {win_rate:.1f}%")
        print(f"   💰 Загальний PnL: {total_pnl:.2f}%")
        
    except Exception as e:
        print(f"❌ Помилка статистики: {e}")
    finally:
        db.close()

def main():
    """Головна функція реальної віртуальної торгівлі"""
    print("🚀 ЗАПУСК РЕАЛЬНОЇ ВІРТУАЛЬНОЇ ТОРГІВЛІ")
    print("=" * 70)
    print("📊 Фаза 2: Тестування REAL AI сигналів (BTC, ETH, SOL, UNI, ...)")
    print("⏰ Оновлення кожні 60 секунд")
    print("🤖 Генерація сигналів кожні 5 хвилин")
    print("🛑 Ctrl+C для зупинки")
    print("-" * 70)
    
    # Очищаємо тестові дані
    print("\n🧹 Очищення тестових даних...")
    try:
        with open('backend/clean_test_data.py', 'r', encoding='utf-8') as f:
            exec(f.read())
    except Exception as e:
        print(f"⚠️ Помилка очищення: {e}")
        print("Продовжуємо без очищення...")
    
    # Перше оновлення
    update_all_real_trades()
    show_statistics()
    
    # Налаштовуємо розклад
    schedule.every(60).seconds.do(update_all_real_trades)  # Оновлення цін
    schedule.every(5).minutes.do(generate_ai_signals_and_trades)  # Генерація сигналів
    schedule.every(2).minutes.do(show_statistics)  # Статистика
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Реальна віртуальна торгівля зупинена")
        print("📊 Фаза 2 успішно завершена!")

if __name__ == "__main__":
    main()