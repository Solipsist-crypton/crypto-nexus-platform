from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import aiohttp
import asyncio
import logging
import random

from app.database import get_db
from app.futures.models import VirtualTrade

router = APIRouter(prefix="", tags=["history"])  # Без префіксу
logger = logging.getLogger(__name__)

class BinanceHistoryClient:
    """Клієнт для отримання історичних даних з Binance"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 24):
        """Отримати останні N свічок"""
        try:
            # Конвертуємо формат символу
            clean_symbol = self._clean_symbol(symbol)
            
            url = f"{self.base_url}/klines"
            params = {
                "symbol": clean_symbol,
                "interval": interval,
                "limit": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_klines(data)
                    else:
                        logger.warning(f"Binance API error for {symbol}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return None
    
    def _clean_symbol(self, symbol: str) -> str:
        """Очистити символ для Binance API"""
        # Видаляємо все після : та замінюємо /
        clean = symbol.split(':')[0].replace('/', '').upper()
        # Додаємо USDT якщо потрібно
        if 'USDT' not in clean:
            clean = f"{clean}USDT"
        return clean
    
    def _format_klines(self, klines_data):
        """Форматування даних для фронтенда"""
        formatted = []
        for kline in klines_data:
            formatted.append({
                "time": datetime.fromtimestamp(kline[0] / 1000).isoformat(),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "price": float(kline[4])  # Додаємо для сумісності
            })
        return formatted

# ЗМІНА ТУТ: замінив "/trade/{trade_id}" на "/data/{trade_id}"
@router.get("/data/{trade_id}")
async def get_trade_history(
    trade_id: int,
    interval: str = "1h",
    limit: int = 24,
    db: Session = Depends(get_db)
):
    """
    Отримати історичні дані для конкретної угоди
    """
    # Знаходимо угоду
    trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Угоду не знайдено")
    
    # Отримуємо історичні дані з Binance
    client = BinanceHistoryClient()
    history = await client.get_klines(
        symbol=trade.symbol,
        interval=interval,
        limit=limit
    )
    
    use_fallback = False
    if not history:
        # Якщо Binance не відповідає, генеруємо демо-дані
        history = generate_fallback_history(trade, interval, limit)
        use_fallback = True
    
    return {
        "trade_id": trade.id,
        "symbol": trade.symbol,
        "entry_price": trade.entry_price,
        "current_price": trade.current_price,
        "take_profit": trade.take_profit,
        "stop_loss": trade.stop_loss,
        "direction": trade.direction,
        "pnl_percentage": trade.pnl_percentage if hasattr(trade, 'pnl_percentage') else 0,
        "created_at": trade.created_at.isoformat() if trade.created_at else None,
        "history": history,
        "data_source": "binance" if not use_fallback else "fallback",
        "timeframe": interval,
        "last_update": datetime.utcnow().isoformat()
    }

def generate_fallback_history(trade, interval, limit):
    """Генерація фейкових даних як fallback"""
    history = []
    base_price = trade.entry_price
    
    # Визначаємо волатильність залежно від монети
    symbol = trade.symbol.split('/')[0] if '/' in trade.symbol else trade.symbol
    volatility = {
        'BTC': 0.015, 'ETH': 0.020, 'SOL': 0.030,
        'XRP': 0.025, 'ADA': 0.028, 'BNB': 0.018,
        'AVAX': 0.035, 'DOGE': 0.045, 'LINK': 0.025
    }.get(symbol.upper(), 0.025)
    
    # Генеруємо тренд відповідно до напрямку
    trend = 0.01 if trade.direction == 'long' else -0.01
    
    # Визначаємо часовий інтервал у годинах
    hours_per_interval = {
        "1h": 1,
        "4h": 4,
        "1d": 24
    }.get(interval, 1)
    
    for i in range(limit):
        # Реалістичний рух ціни
        random_walk = (random.random() - 0.5) * 2 * volatility
        price_change = trend + random_walk
        price = base_price * (1 + price_change)
        
        # Додаємо волатильність всередині свічки
        open_price = price * (1 - volatility/4)
        high_price = price * (1 + volatility/3)
        low_price = price * (1 - volatility/3)
        close_price = price
        
        history.append({
            "time": (datetime.utcnow() - timedelta(hours=hours_per_interval*(limit-i))).isoformat(),
            "open": round(open_price, 4),
            "high": round(high_price, 4),
            "low": round(low_price, 4),
            "close": round(close_price, 4),
            "price": round(close_price, 4),
            "volume": round(random.uniform(1000, 10000), 2)
        })
    
    return history