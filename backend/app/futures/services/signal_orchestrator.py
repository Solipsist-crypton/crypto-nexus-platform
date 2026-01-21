"""
AISignalOrchestrator - пайплайн для автоматичної генерації сигналів
(Фаза 1 з roadmap: "пайплайн, який раз на годину генерує нові сигнали")
"""

from datetime import datetime, timedelta
from typing import List
from celery import Celery
import os



celery_app = Celery(
    'signal_orchestrator',
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

class AISignalOrchestrator:
    """Оркестратор для автоматичної генерації сигналів"""
    
    def __init__(self):
        from app.futures.services.ai_analyzer import AIAnalyzer
        self.ai_analyzer = AIAnalyzer()
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOTUSDT"]
        self.timeframes = ["1h", "4h", "1d"]
        self.ai_analyzer = AIAnalyzer()
    
    def generate_daily_signals(self) -> List[dict]:
        """Генерувати сигнали для всіх символів та таймфреймів"""
        signals = []
        
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                try:
                    # Аналіз ринку
                    analysis = self.ai_analyzer.analyze_market(symbol, timeframe)
                    
                    # Фільтр за confidence
                    if analysis["confidence"] > 0.65:
                        signals.append({
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "analysis": analysis,
                            "generated_at": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    print(f"Error analyzing {symbol} {timeframe}: {e}")
        
        return signals
    
    def save_signals_to_db(self, signals: List[dict]):
        """Зберегти згенеровані сигнали в БД"""
        from app.database import SessionLocal
        from app.futures.models import Signal
        from app.futures.services.explanation_builder import explanation_builder
        
        db = SessionLocal()
        
        for signal_data in signals:
            try:
                analysis = signal_data["analysis"]
                explanation = explanation_builder.build_explanation(
                    symbol=signal_data["symbol"],
                    direction=analysis["direction"],
                    confidence=analysis["confidence"],
                    factors=analysis["factors"]
                )
                
                db_signal = Signal(
                    symbol=signal_data["symbol"],
                    direction=analysis["direction"],
                    confidence=analysis["confidence"],
                    reasoning_weights=analysis["factors"],
                    explanation_text=explanation,
                    entry_price=analysis["entry_price"],
                    take_profit=analysis["take_profit"],
                    stop_loss=analysis["stop_loss"],
                    timeframe=signal_data["timeframe"],
                    is_active=True,
                    source="orchestrator_v1"
                )
                
                db.add(db_signal)
                
            except Exception as e:
                print(f"Error saving signal: {e}")
        
        db.commit()
        db.close()

@celery_app.task
def run_daily_signal_generation():
    from app.futures.services.ai_analyzer import AIAnalyzer
    """Celery задача для щоденної генерації сигналів"""
    print(f"[{datetime.now()}] Starting daily signal generation...")
    
    orchestrator = AISignalOrchestrator()
    signals = orchestrator.generate_daily_signals()
    
    print(f"Generated {len(signals)} signals")
    
    if signals:
        orchestrator.save_signals_to_db(signals)
        print(f"Saved {len(signals)} signals to database")
    
    return {
        "status": "success",
        "generated": len(signals),
        "timestamp": datetime.now().isoformat()
    }

# Планувальник: запускати кожну годину
celery_app.conf.beat_schedule = {
    'generate-daily-signals': {
        'task': 'backend.app.futures.services.signal_orchestrator.run_daily_signal_generation',
        'schedule': 3600.0,  # Кожну годину
    },
}