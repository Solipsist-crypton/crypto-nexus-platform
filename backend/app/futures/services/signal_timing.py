# backend/app/futures/services/signal_timing.py
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.futures.models import Signal

class SignalTimingService:
    """Сервіс для керування таймінгами сигналів без зміни моделей"""
    
    @staticmethod
    def calculate_timing(signal: Signal) -> Dict:
        """Розрахувати таймінги для сигналу"""
        if not signal.created_at:
            return {}
        
        # Налаштування за замовчуванням
        DEFAULT_EXPIRATION = 30  # 30 хвилин
        DEFAULT_BEST_WINDOW = 5  # 5 хвилин на кращий вхід
        
        # Адаптуємо на основі confidence
        expiration_minutes = DEFAULT_EXPIRATION
        if signal.confidence > 0.8:
            expiration_minutes = 45  # Сильні сигнали діють довше
        elif signal.confidence < 0.6:
            expiration_minutes = 20  # Слабкі сигнали діють менше
        
        # Розраховуємо час
        time_passed = datetime.utcnow() - signal.created_at
        minutes_passed = time_passed.total_seconds() / 60
        minutes_remaining = max(0, expiration_minutes - minutes_passed)
        
        # Статуси
        is_expired = minutes_remaining <= 0
        in_best_window = minutes_passed <= DEFAULT_BEST_WINDOW
        is_still_valid = not is_expired
        
        return {
            "expiration_minutes": expiration_minutes,
            "minutes_remaining": int(minutes_remaining),
            "minutes_passed": int(minutes_passed),
            "is_expired": is_expired,
            "in_best_window": in_best_window,
            "is_still_valid": is_still_valid,
            "best_window_minutes": DEFAULT_BEST_WINDOW,
            "created_at_iso": signal.created_at.isoformat() if signal.created_at else None,
            "expires_at_iso": (signal.created_at + timedelta(minutes=expiration_minutes)).isoformat() if signal.created_at else None,
            "urgency_level": SignalTimingService._calculate_urgency(minutes_remaining, in_best_window)
        }
    
    @staticmethod
    def _calculate_urgency(minutes_remaining: float, in_best_window: bool) -> str:
        """Розрахувати рівень терміновості"""
        if minutes_remaining <= 0:
            return "expired"
        elif minutes_remaining <= 5:
            return "urgent"
        elif in_best_window:
            return "optimal"
        elif minutes_remaining <= 15:
            return "soon"
        else:
            return "normal"
    
    @staticmethod
    def get_active_signals(db: Session, user_id: int = 1) -> Dict:
        """Отримати активні сигнали для користувача"""
        # Знаходимо всі сигнали
        all_signals = db.query(Signal).filter(
            Signal.is_active == True
        ).order_by(
            Signal.confidence.desc(),
            Signal.created_at.desc()
        ).all()
        
        # Класифікуємо за таймінгами
        active_signals = []
        expired_signals = []
        
        for signal in all_signals:
            timing = SignalTimingService.calculate_timing(signal)
            
            signal_data = {
                **signal.to_dict(),
                "timing": timing
            }
            
            if timing["is_still_valid"]:
                active_signals.append(signal_data)
            else:
                expired_signals.append(signal_data)
        
        return {
            "active": active_signals,
            "expired": expired_signals,
            "counts": {
                "total": len(all_signals),
                "active": len(active_signals),
                "expired": len(expired_signals)
            }
        }
    
    @staticmethod
    def create_timed_trade(db: Session, signal_id: int, user_id: int = 1) -> Optional[Dict]:
        """Створити угоду з перевіркою таймінгу"""
        from ..services.trade_executor import VirtualTradeExecutor
        
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            return {"error": "Signal not found"}
        
        timing = SignalTimingService.calculate_timing(signal)
        
        # Перевіряємо чи сигнал ще актуальний
        if not timing["is_still_valid"]:
            return {
                "error": "Signal expired",
                "message": f"Signal expired {timing['minutes_passed']} minutes ago",
                "timing": timing
            }
        
        # Перевіряємо чи користувач вже має угоду для цього сигналу
        from ...models import VirtualTrade
        existing_trade = db.query(VirtualTrade).filter(
            VirtualTrade.signal_id == signal_id,
            VirtualTrade.user_id == user_id
        ).first()
        
        if existing_trade:
            return {
                "error": "Trade already exists",
                "trade_id": existing_trade.id,
                "timing": timing
            }
        
        # Створюємо нову угоду
        executor = VirtualTradeExecutor()
        trade = executor.create_virtual_trade(db, signal_id, user_id)
        
        if trade:
            return {
                "success": True,
                "message": "Trade created successfully",
                "trade_id": trade.id,
                "timing": timing,
                "trade": trade.to_dict()
            }
        else:
            return {"error": "Failed to create trade"}