import aiohttp
from typing import Dict, Optional

class CoinbaseClient:
    def __init__(self):
        self.base_url = "https://api.coinbase.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                # Для Coinbase: BTC-USD -> btc-usd
                product_id = symbol.replace("-", "").lower()
                url = f"{self.base_url}/api/v3/brokerage/products/{product_id}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "price": float(data.get("price", 0)),
                            "exchange": "Coinbase",
                            "symbol": symbol
                        }
        except Exception as e:
            print(f"Coinbase API error: {e}")
        return None