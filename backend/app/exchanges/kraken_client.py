import httpx
import asyncio
from typing import Optional, Dict

class KrakenClient:
    BASE_URL = "https://api.kraken.com/0/public"
    
    async def get_price(self, pair: str = "XXBTZUSD") -> Optional[Dict]:
        """
        Отримати поточну ціну з Kraken
        pair: XXBTZUSD (BTC/USD), XETHZUSD (ETH/USD), SOLUSD тощо
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.BASE_URL}/Ticker", params={"pair": pair})
                response.raise_for_status()
                data = response.json()
                
                if "result" in data and pair in data["result"]:
                    ticker = data["result"][pair]
                    return {
                        "symbol": pair,
                        "price": float(ticker["c"][0]),  # остання ціна закриття
                        "exchange": "Kraken",
                        "volume": float(ticker["v"][1]) if len(ticker["v"]) > 1 else 0
                    }
                return None
                
        except Exception as e:
            print(f"❌ Помилка отримання ціни з Kraken для {pair}: {e}")
            return None
    
    async def get_prices(self, pairs: list = None) -> Dict[str, float]:
        """
        Отримати ціни для кількох пар
        """
        if pairs is None:
            pairs = ["XXBTZUSD", "XETHZUSD", "SOLUSD"]  # BTC, ETH, SOL в USD
            
        tasks = [self.get_price(pair) for pair in pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        symbol_map = {
            "XXBTZUSD": "BTC",
            "XETHZUSD": "ETH", 
            "SOLUSD": "SOL"
        }
        
        for pair, result in zip(pairs, results):
            if isinstance(result, dict) and "price" in result:
                coin = symbol_map.get(pair, pair)
                prices[coin] = result["price"]
        
        return prices