from fastapi import APIRouter, HTTPException
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class BinanceClient:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"

    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Binance"""
        try:
            url = f"{self.base_url}/ticker/price?symbol={symbol}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'price': float(data['price']),
                            'exchange': 'Binance',
                            'symbol': symbol,
                            'timestamp': data.get('time', '')
                        }
                    else:
                        logger.error(f"Binance API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching price from Binance: {e}")
            return None

    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Отримати детальну інформацію про тикер"""
        try:
            url = f"{self.base_url}/ticker/24hr?symbol={symbol}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            logger.error(f"Error fetching ticker from Binance: {e}")
            return None


# Ініціалізація клієнта
client = BinanceClient()


@router.get("/health")
async def health_check():
    """Перевірка стану Binance API"""
    try:
        price = await client.get_price("BTCUSDT")
        return {
            "status": "healthy" if price else "unhealthy",
            "exchange": "Binance",
            "timestamp": price.get('timestamp') if price else None
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """Отримати поточну ціну для символу"""
    price_data = await client.get_price(symbol)
    if not price_data:
        raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
    
    return {
        "success": True,
        "data": price_data,
        "message": f"Ціна {symbol} отримана з Binance"
    }


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Отримати детальну інформацію про тикер"""
    ticker_data = await client.get_ticker(symbol)
    if not ticker_data:
        raise HTTPException(status_code=404, detail=f"Ticker not found for {symbol}")
    
    return {
        "success": True,
        "data": ticker_data,
        "message": f"Ticker {symbol} отриманий з Binance"
    }


@router.get("/symbols")
async def get_top_symbols(limit: int = 20):
    """Отримати список популярних символів"""
    try:
        url = f"{client.base_url}/ticker/24hr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    tickers = await response.json()
                    # Сортуємо за обсягом торгів
                    sorted_tickers = sorted(
                        tickers,
                        key=lambda x: float(x.get('quoteVolume', 0)),
                        reverse=True
                    )[:limit]
                    return {
                        "success": True,
                        "data": sorted_tickers,
                        "count": len(sorted_tickers)
                    }
                return {"success": False, "error": "Failed to fetch symbols"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))