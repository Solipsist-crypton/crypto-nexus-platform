import asyncio
from typing import List, Dict, Optional
from app.exchanges.binance_client import BinanceClient
from app.exchanges.kraken_client import KrakenClient
from datetime import datetime

class ArbitrageCalculator:
    def __init__(self):
        self.binance = BinanceClient()
        self.kraken = KrakenClient()
        
    async def compare_prices(self, coin: str = "BTC") -> Dict:
        """
        Порівняти ціни на Binance та Kraken
        """
        # Мапимо назви монет до символів бірж
        symbol_map = {
            "BTC": {"binance": "BTCUSDT", "kraken": "XXBTZUSD"},
            "ETH": {"binance": "ETHUSDT", "kraken": "XETHZUSD"},
            "SOL": {"binance": "SOLUSDT", "kraken": "SOLUSD"}
        }
        
        if coin not in symbol_map:
            return {"error": f"Монета {coin} не підтримується"}
        
        # Отримуємо ціни з обох бірж
        binance_price = await self.binance.get_price(symbol_map[coin]["binance"])
        kraken_price = await self.kraken.get_price(symbol_map[coin]["kraken"])
        
        if not binance_price or not kraken_price:
            return {"error": "Не вдалося отримати ціни"}
        
        # Конвертуємо в числа
        price_binance = binance_price["price"]
        price_kraken = kraken_price["price"]
        
        # Розраховуємо різницю
        difference = price_kraken - price_binance
        difference_percent = (difference / price_binance) * 100
        
        # Комісії бірж (в %)
        # Binance: 0.1% maker/taker для spot
        # Kraken: 0.16% maker, 0.26% taker для spot
        commission_binance = 0.001  # 0.1%
        commission_kraken = 0.0026  # 0.26% (беремо taker для консервативності)
        
        # Розрахунок реального прибутку після комісій
        total_commission = commission_binance + commission_kraken
        
        # Якщо купуємо на Binance (дешевше) і продаємо на Kraken (дорожче)
        if price_binance < price_kraken:
            potential_profit_percent = difference_percent - (total_commission * 100)
            direction = "Binance → Kraken"
            buy_price = price_binance
            sell_price = price_kraken
            buy_exchange = "Binance"
            sell_exchange = "Kraken"
        else:
            # Якщо купуємо на Kraken і продаємо на Binance
            difference_percent = (price_binance - price_kraken) / price_kraken * 100
            potential_profit_percent = difference_percent - (total_commission * 100)
            direction = "Kraken → Binance"
            buy_price = price_kraken
            sell_price = price_binance
            buy_exchange = "Kraken"
            sell_exchange = "Binance"
        
        return {
            "coin": coin,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "buy_price": round(buy_price, 2),
            "sell_price": round(sell_price, 2),
            "price_difference": round(difference, 2),
            "price_difference_percent": round(abs(difference_percent), 4),
            "commission_binance": f"{commission_binance * 100}%",
            "commission_kraken": f"{commission_kraken * 100}%",
            "total_commission": f"{total_commission * 100}%",
            "potential_profit_percent": round(potential_profit_percent, 4),
            "is_profitable": potential_profit_percent > 0.1,  # > 0.1% після комісій
            "direction": direction,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def scan_all_coins(self) -> List[Dict]:
        """
        Сканувати всі доступні монети
        """
        coins = ["BTC", "ETH", "SOL"]
        tasks = [self.compare_prices(coin) for coin in coins]
        results = await asyncio.gather(*tasks)
        
        # Фільтруємо помилки
        return [r for r in results if "error" not in r]
    
    async def find_best_opportunity(self) -> Optional[Dict]:
        """
        Знайти найкращу арбітражну можливість
        """
        opportunities = await self.scan_all_coins()
        if not opportunities:
            return None
        
        # Сортуємо по потенційному прибутку (за спаданням)
        opportunities.sort(key=lambda x: x["potential_profit_percent"], reverse=True)
        return opportunities[0]