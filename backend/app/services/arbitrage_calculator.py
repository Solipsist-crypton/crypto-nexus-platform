import asyncio
from typing import List, Dict, Optional, Tuple
from app.exchanges.binance_client import BinanceClient
from app.exchanges.kraken_client import KrakenClient
from datetime import datetime

class ArbitrageCalculator:
    def __init__(self):
        self.binance = BinanceClient()
        self.kraken = KrakenClient()
        
        # Мапи символів для різних бірж
        self.symbol_map = {
            "BTC": {"binance": "BTCUSDT", "kraken": "XXBTZUSD"},
            "ETH": {"binance": "ETHUSDT", "kraken": "XETHZUSD"},
            "SOL": {"binance": "SOLUSDT", "kraken": "SOLUSD"}
        }
        
        # Базові комісії (будуть оновлені реальними даними)
        self.base_fees = {
            "Binance": {"maker": 0.001, "taker": 0.001},      # 0.1%
            "Kraken": {"maker": 0.0016, "taker": 0.0026}      # 0.16% maker, 0.26% taker
        }
        
        # Підтримувані монети
        self.supported_coins = ["BTC", "ETH", "SOL"]

    # ==================== ОСНОВНА ЛОГІКА ====================

    async def compare_prices(self, coin: str = "BTC") -> Dict:
        """
        Порівняти ціни на Binance та Kraken для однієї монети
        Повертає детальний аналіз арбітражної можливості
        """
        # Перевірка підтримки монети
        if coin not in self.supported_coins:
            return self._error_response(f"Монета {coin} не підтримується")
        
        # Отримання цін з обох бірж
        binance_price, kraken_price = await self._fetch_prices(coin)
        
        if not binance_price or not kraken_price:
            return self._error_response("Не вдалося отримати ціни з бірж")
        
        # Аналіз арбітражної можливості
        return await self._analyze_arbitrage(coin, binance_price, kraken_price)

    async def scan_all_coins(self) -> List[Dict]:
        """
        Сканувати всі доступні монети
        Повертає список арбітражних можливостей
        """
        tasks = [self.compare_prices(coin) for coin in self.supported_coins]
        results = await asyncio.gather(*tasks)
        
        # Фільтруємо успішні результати (без помилок)
        successful_results = []
        for result in results:
            if "error" not in result and result.get("is_opportunity", False):
                successful_results.append(result)
        
        # Сортуємо за потенційним прибутком (спадання)
        successful_results.sort(key=lambda x: x.get("potential_profit_percent", 0), reverse=True)
        
        return successful_results

    async def find_best_opportunity(self) -> Optional[Dict]:
        """
        Знайти найкращу арбітражну можливість
        """
        opportunities = await self.scan_all_coins()
        return opportunities[0] if opportunities else None

    # ==================== ДОПОМІЖНІ МЕТОДИ ====================

    async def _fetch_prices(self, coin: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Отримати ціни з Binance та Kraken
        """
        binance_symbol = self.symbol_map[coin]["binance"]
        kraken_symbol = self.symbol_map[coin]["kraken"]
        
        try:
            binance_task = self.binance.get_price(binance_symbol)
            kraken_task = self.kraken.get_price(kraken_symbol)
            
            binance_price, kraken_price = await asyncio.gather(binance_task, kraken_task)
            return binance_price, kraken_price
            
        except Exception as e:
            print(f"Помилка отримання цін для {coin}: {e}")
            return None, None

    async def _analyze_arbitrage(self, coin: str, binance_data: Dict, kraken_data: Dict) -> Dict:
        """
        Проаналізувати арбітражну можливість між двома біржами
        """
        # Ціни
        price_binance = binance_data["price"]
        price_kraken = kraken_data["price"]
        
        # Визначаємо напрямок торгівлі
        if price_binance < price_kraken:
            # Купуємо на Binance, продаємо на Kraken
            direction = "Binance → Kraken"
            buy_exchange = "Binance"
            sell_exchange = "Kraken"
            buy_price = price_binance
            sell_price = price_kraken
            price_difference = price_kraken - price_binance
            price_difference_percent = (price_difference / price_binance) * 100
        else:
            # Купуємо на Kraken, продаємо на Binance
            direction = "Kraken → Binance"
            buy_exchange = "Kraken"
            sell_exchange = "Binance"
            buy_price = price_kraken
            sell_price = price_binance
            price_difference = price_binance - price_kraken
            price_difference_percent = (price_difference / price_kraken) * 100
        
        # Комісії (за замовчуванням taker)
        buy_commission = self.base_fees[buy_exchange]["taker"]
        sell_commission = self.base_fees[sell_exchange]["taker"]
        total_commission = buy_commission + sell_commission
        
        # Потенційний прибуток після комісій
        potential_profit_percent = price_difference_percent - (total_commission * 100)
        
        # Критерій прибутковості (можна налаштувати)
        min_profit_threshold = 0.1  # 0.1% мінімальний прибуток
        is_profitable = potential_profit_percent > min_profit_threshold
        
        # Класифікація можливості
        opportunity_type = self._classify_opportunity(potential_profit_percent)
        
        # Формуємо відповідь
        return {
            # Основна інформація
            "coin": coin,
            "direction": direction,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            
            # Ціни
            "buy_price": round(buy_price, 2),
            "sell_price": round(sell_price, 2),
            "price_difference": round(price_difference, 2),
            "price_difference_percent": round(price_difference_percent, 4),
            
            # Комісії
            "buy_commission_percent": round(buy_commission * 100, 3),
            "sell_commission_percent": round(sell_commission * 100, 3),
            "total_commission_percent": round(total_commission * 100, 3),
            
            # Прибутковість
            "potential_profit_percent": round(potential_profit_percent, 4),
            "is_profitable": is_profitable,
            "opportunity_type": opportunity_type,
            "min_profit_threshold": min_profit_threshold,
            
            # Метадані
            "timestamp": datetime.utcnow().isoformat(),
            "is_opportunity": is_profitable,
            
            # Символи
            "binance_symbol": self.symbol_map[coin]["binance"],
            "kraken_symbol": self.symbol_map[coin]["kraken"],
            
            # Додаткова інформація з бірж
            "binance_data": {
                "price": price_binance,
                "exchange": binance_data.get("exchange", "Binance"),
                "timestamp": binance_data.get("timestamp")
            },
            "kraken_data": {
                "price": price_kraken,
                "exchange": kraken_data.get("exchange", "Kraken"),
                "volume": kraken_data.get("volume", 0),
                "timestamp": kraken_data.get("timestamp")
            }
        }

    def _classify_opportunity(self, profit_percent: float) -> str:
        """
        Класифікувати арбітражну можливість за прибутковістю
        """
        if profit_percent > 1.0:
            return "EXCELLENT"      # Відмінно: > 1%
        elif profit_percent > 0.5:
            return "GOOD"           # Добре: 0.5% - 1%
        elif profit_percent > 0.2:
            return "AVERAGE"        # Середньо: 0.2% - 0.5%
        elif profit_percent > 0.1:
            return "MARGINAL"       # Мінімально: 0.1% - 0.2%
        else:
            return "UNPROFITABLE"   # Неприбутково

    def _error_response(self, message: str) -> Dict:
        """
        Формування відповіді з помилкою
        """
        return {
            "error": message,
            "success": False,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ==================== УТИЛІТИ ====================

    def update_fees(self, exchange: str, maker_fee: float, taker_fee: float):
        """
        Оновити комісії біржі
        """
        if exchange in self.base_fees:
            self.base_fees[exchange]["maker"] = maker_fee
            self.base_fees[exchange]["taker"] = taker_fee
            print(f"Оновлено комісії для {exchange}: maker={maker_fee*100}%, taker={taker_fee*100}%")

    def add_coin(self, coin: str, binance_symbol: str, kraken_symbol: str):
        """
        Додати нову монету для моніторингу
        """
        self.symbol_map[coin] = {
            "binance": binance_symbol,
            "kraken": kraken_symbol
        }
        self.supported_coins.append(coin)
        print(f"Додано монету {coin}: Binance={binance_symbol}, Kraken={kraken_symbol}")

    def get_supported_coins(self) -> List[str]:
        """
        Отримати список підтримуваних монет
        """
        return self.supported_coins.copy()

    def get_exchange_fees(self, exchange: str) -> Dict:
        """
        Отримати поточні комісії біржі
        """
        return self.base_fees.get(exchange, {}).copy()