import httpx
import asyncio
from typing import Optional, Dict

class BinanceClient:
    BASE_URL = "https://api.binance.com/api/v3"
    
    async def get_price(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        Отримати поточну ціну з Binance
        symbol: BTCUSDT, ETHUSDT, SOLUSDT тощо
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.BASE_URL}/ticker/price", params={"symbol": symbol})
                response.raise_for_status()
                data = response.json()
                
                return {
                    "symbol": data["symbol"],
                    "price": float(data["price"]),
                    "exchange": "Binance",
                    "timestamp": data.get("time", None)  # якщо є
                }
        except Exception as e:
            print(f"❌ Помилка отримання ціни з Binance для {symbol}: {e}")
            return None
    
    async def get_prices(self, symbols: list = None) -> Dict[str, float]:
        """
        Отримати ціни для кількох пар одночасно
        """
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        tasks = [self.get_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, dict) and "price" in result:
                prices[symbol.replace("USDT", "")] = result["price"]
        
        return prices