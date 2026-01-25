# backend/app/futures/services/trade_executor.py
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..models import VirtualTrade, Signal
from app.futures.models.exchange_connector import ExchangeConnector
import logging

class VirtualTradeExecutor:
    """Виконавець віртуальних угод"""
    
    def __init__(self):
        self.exchange = ExchangeConnector()
        self.logger = logging.getLogger(__name__)
    
    def create_virtual_trade(self, db: Session, signal_id: int, user_id: int) -> Optional[VirtualTrade]:
        """Створення віртуальної угоди на основі сигналу"""
        try:
            # Отримуємо сигнал
            signal = db.query(Signal).filter(Signal.id == signal_id).first()
            if not signal:
                self.logger.error(f"Сигнал {signal_id} не знайдено")
                return None
            
            # Створюємо віртуальну угоду
            virtual_trade = VirtualTrade(
                user_id=user_id,
                signal_id=signal_id,
                symbol=signal.symbol,
                direction=signal.direction,
                entry_price=signal.entry_price,
                take_profit=signal.take_profit,
                stop_loss=signal.stop_loss,
                current_price=signal.entry_price,
                status="active"
            )
            
            db.add(virtual_trade)
            db.commit()
            db.refresh(virtual_trade)
            
            self.logger.info(f"Створено віртуальну угоду {virtual_trade.id} для сигналу {signal_id}")
            return virtual_trade
            
        except Exception as e:
            self.logger.error(f"Помилка створення віртуальної угоди: {e}")
            db.rollback()
            return None
    
    def update_trade_prices(self, db: Session, trade_id: int) -> Optional[Dict]:
        """Оновлення ціни та розрахунок PnL для угоди"""
        try:
            trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
            if not trade or trade.status != "active":
                return None
            
            # Отримуємо поточну ціну
            ticker = self.exchange.fetch_ticker(trade.symbol)
            if not ticker:
                return None
            
            current_price = ticker['last']
            old_status = trade.status
            
            # Розраховуємо PnL
            trade.calculate_pnl(current_price)
            
            # Якщо статус змінився (TP/SL досягнуто)
            if trade.status != old_status and trade.status in ["tp_hit", "sl_hit"]:
                trade.closed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(trade)
            
            return {
                "trade": trade.to_dict(),
                "price_updated": current_price,
                "status_changed": trade.status != old_status
            }
            
        except Exception as e:
            self.logger.error(f"Помилка оновлення угоди {trade_id}: {e}")
            return None
    
    def update_all_active_trades(self, db: Session) -> Dict:
        """Оновлення всіх активних угод"""
        active_trades = db.query(VirtualTrade).filter(VirtualTrade.status == "active").all()
        
        results = {
            "total": len(active_trades),
            "updated": 0,
            "tp_hit": 0,
            "sl_hit": 0,
            "errors": 0
        }
        
        for trade in active_trades:
            try:
                result = self.update_trade_prices(db, trade.id)
                if result:
                    results["updated"] += 1
                    if result["status_changed"]:
                        if trade.status == "tp_hit":
                            results["tp_hit"] += 1
                        elif trade.status == "sl_hit":
                            results["sl_hit"] += 1
            except Exception as e:
                results["errors"] += 1
                self.logger.error(f"Помилка оновлення угоди {trade.id}: {e}")
        
        return results