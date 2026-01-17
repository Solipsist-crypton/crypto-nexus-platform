"""
ШАБЛОН ДЛЯ НОВОЇ БІРЖІ
Копіюй цей файл, заміни {EXCHANGE_NAME} на назву біржі
"""

from fastapi import APIRouter, HTTPException
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class {EXCHANGE_NAME}Client:  # Наприклад: GateIOClient
    """Клієнт для роботи з API біржі {EXCHANGE_NAME}"""
    
    def __init__(self):
        # ЗАМІНИ URL API біржі
        self.base_url = "https://api.{exchange}.com/api/v4"  # Приклад
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з біржі {EXCHANGE_NAME}"""
        try:
            # ЗАМІНИ ЕНДПОЇНТ та параметри запиту
            url = f"{self.base_url}/spot/tickers?currency_pair={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # ЗАМІНИ ЛОГІКУ ПАРСИНГУ ВІДПОВІДІ
                        # Кожна біржа має свою структуру відповіді
                        # Знайди поле з ціною в документації API
                        price = float(data[0]['last'])
                        
                        return {
                            'price': price,
                            'exchange': '{EXCHANGE_NAME}',  # Назва біржі
                            'symbol': symbol,
                            'timestamp': data[0].get('timestamp', '')
                        }
                    else:
                        logger.error(f"{EXCHANGE_NAME} API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching price from {EXCHANGE_NAME}: {e}")
            return None


# Ініціалізація клієнта
client = {EXCHANGE_NAME}Client()


# ОБОВ'ЯЗКОВІ ЕНДПОЇНТИ ДЛЯ КОЖНОЇ БІРЖІ
@router.get("/health")
async def health_check():
    """Перевірка стану API біржі"""
    try:
        # ЗАМІНИ ТЕСТОВИЙ СИМВОЛ
        price = await client.get_price("BTC_USDT")  
        return {
            "status": "healthy" if price else "unhealthy",
            "exchange": "{EXCHANGE_NAME}"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """Отримати поточну ціну для символу"""
    price_data = await client.get_price(symbol)
    
    if not price_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Price not found for {symbol} on {EXCHANGE_NAME}"
        )
    
    return {
        "success": True,
        "data": price_data,
        "message": f"Ціна {symbol} отримана з {EXCHANGE_NAME}"
    }


# ДОДАТКОВІ ЕНДПОЇНТИ (необов'язково)
@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Отримати детальну інформацію про тикер"""
    # Реалізація за потребою
    pass