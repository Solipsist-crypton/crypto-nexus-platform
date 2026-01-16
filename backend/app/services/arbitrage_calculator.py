import asyncio
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

# Імпортуємо клієнти для всіх бірж
from app.exchanges.binance_client import BinanceClient
from app.exchanges.kraken_client import KrakenClient
from app.exchanges.coinbase_client import CoinbaseClient
from app.exchanges.bybit_client import BybitClient
from app.exchanges.okx_client import OKXClient

from app.config.fees_config import get_trading_fee, get_withdrawal_fee, set_fee_mode, update_fee

class ArbitrageCalculator:
    def __init__(self):
        # Ініціалізація всіх клієнтів бірж
        self.exchanges = {
            "Binance": BinanceClient(),
            "Kraken": KrakenClient(),
            "Coinbase": CoinbaseClient(),
            "Bybit": BybitClient(),
            "OKX": OKXClient()
        }
        
        # Мапи символів для всіх бірж
        self.symbol_map = {
            "BTC": {
                "Binance": "BTCUSDT",
                "Kraken": "XXBTZUSD", 
                "Coinbase": "BTC-USD",
                "Bybit": "BTCUSDT",
                "OKX": "BTC-USDT"
            },
            "ETH": {
                "Binance": "ETHUSDT",
                "Kraken": "XETHZUSD",
                "Coinbase": "ETH-USD",
                "Bybit": "ETHUSDT", 
                "OKX": "ETH-USDT"
            },
            "SOL": {
                "Binance": "SOLUSDT",
                "Kraken": "SOLUSD",
                "Coinbase": "SOL-USD",
                "Bybit": "SOLUSDT",
                "OKX": "SOL-USDT"
            },
            "BNB": {
                "Binance": "BNBUSDT",
                "Kraken": "BNBUSD",
                "Coinbase": "BNB-USD",
                "Bybit": "BNBUSDT",
                "OKX": "BNB-USDT"
            },
            "XRP": {
                "Binance": "XRPUSDT",
                "Kraken": "XXRPZUSD",
                "Coinbase": "XRP-USD",
                "Bybit": "XRPUSDT",
                "OKX": "XRP-USDT"
            },
            "ADA": {
                "Binance": "ADAUSDT",
                "Kraken": "ADAUSD",
                "Coinbase": "ADA-USD",
                "Bybit": "ADAUSDT",
                "OKX": "ADA-USDT"
            },
            "DOT": {
                "Binance": "DOTUSDT",
                "Kraken": "DOTUSD",
                "Coinbase": "DOT-USD",
                "Bybit": "DOTUSDT",
                "OKX": "DOT-USDT"
            },
            "DOGE": {
                "Binance": "DOGEUSDT",
                "Kraken": "XDGUSD",
                "Coinbase": "DOGE-USD",
                "Bybit": "DOGEUSDT",
                "OKX": "DOGE-USDT"
            },
            "AVAX": {
                "Binance": "AVAXUSDT",
                "Kraken": "AVAXUSD",
                "Coinbase": "AVAX-USD",
                "Bybit": "AVAXUSDT",
                "OKX": "AVAX-USDT"
            },
            "MATIC": {
                "Binance": "MATICUSDT",
                "Kraken": "MATICUSD",
                "Coinbase": "MATIC-USD",
                "Bybit": "MATICUSDT",
                "OKX": "MATIC-USDT"
            }
        }
        
        # Підтримувані монети (10)
        self.supported_coins = list(self.symbol_map.keys())
        
        # Підтримувані біржі (5)
        self.supported_exchanges = list(self.exchanges.keys())
        
        # Режим комісій
        self.fee_mode = "taker"
        
        # Оцінки ліквідності (тимчасові)
        self._init_liquidity_scores()

    def _init_liquidity_scores(self):
        """Ініціалізація базових оцінок ліквідності"""
        self.liquidity_scores = {
            "Binance": {coin: 0.9 for coin in self.supported_coins},
            "Kraken": {coin: 0.85 for coin in self.supported_coins},
            "Coinbase": {coin: 0.88 for coin in self.supported_coins},
            "Bybit": {coin: 0.82 for coin in self.supported_coins},
            "OKX": {coin: 0.84 for coin in self.supported_coins}
        }

    # ==================== ОСНОВНА ЛОГІКА ====================

    async def compare_prices(self, coin: str = "BTC") -> Dict:
        """
        Порівняти ціни на всіх біржах для однієї монети
        Повертає найкращу арбітражну можливість
        """
        if coin not in self.supported_coins:
            return self._error_response(f"Монета {coin} не підтримується")
        
        # Отримати ціни з усіх бірж
        prices = await self._fetch_all_prices(coin)
        
        if not prices:
            return self._error_response("Не вдалося отримати ціни")
        
        # Знайти найкращу арбітражну пару
        best_opportunity = await self._find_best_arbitrage(coin, prices)
        
        return {
            "coin": coin,
            "prices": prices,
            "best_opportunity": best_opportunity if best_opportunity.get("is_profitable") else None,
            "all_opportunities": self._filter_profitable_opportunities([best_opportunity]),
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        }

    async def scan_all_coins(self) -> List[Dict]:
        """
        Сканувати всі 10 монет на всіх 5 біржах
        """
        all_results = []
        
        for coin in self.supported_coins:
            try:
                result = await self.compare_prices(coin)
                if result.get("success") and result.get("best_opportunity"):
                    all_results.append(result)
            except Exception as e:
                print(f"Помилка сканування {coin}: {e}")
                continue
        
        # Сортування за прибутковістю
        all_results.sort(
            key=lambda x: x.get("best_opportunity", {}).get("net_profit_percent", 0),
            reverse=True
        )
        
        return all_results

    async def find_top_opportunities(self, limit: int = 5) -> List[Dict]:
        """
        Знайти топ N арбітражних можливостей
        """
        all_opps = []
        
        for coin in self.supported_coins:
            prices = await self._fetch_all_prices(coin)
            if prices:
                opportunity = await self._find_best_arbitrage(coin, prices)
                if opportunity.get("is_profitable"):
                    all_opps.append(opportunity)
        
        # Сортуємо та обмежуємо кількість
        all_opps.sort(key=lambda x: x.get("net_profit_percent", 0), reverse=True)
        return all_opps[:limit]

    # ==================== ДОПОМІЖНІ МЕТОДИ ====================

    async def _fetch_all_prices(self, coin: str) -> Dict[str, float]:
        """
        Отримати ціни з усіх 5 бірж для однієї монети
        """
        prices = {}
        
        for exchange_name, client in self.exchanges.items():
            try:
                symbol = self.symbol_map[coin][exchange_name]
                price_data = await client.get_price(symbol)
                
                if price_data and "price" in price_data:
                    prices[exchange_name] = price_data["price"]
                else:
                    prices[exchange_name] = None
                    
            except Exception as e:
                print(f"Помилка отримання ціни з {exchange_name} для {coin}: {e}")
                prices[exchange_name] = None
        
        return prices

    async def _find_best_arbitrage(self, coin: str, prices: Dict[str, float]) -> Dict:
        """
        Знайти найкращу арбітражну пару серед всіх бірж
        """
        best_opportunity = None
        best_profit = -999
        
        # Перебираємо всі можливі пари бірж
        exchanges = [ex for ex in prices.keys() if prices[ex] is not None]
        
        for i, buy_exchange in enumerate(exchanges):
            for sell_exchange in exchanges[i+1:]:
                # Аналізуємо обидва напрямки
                for buy_ex, sell_ex in [(buy_exchange, sell_exchange), (sell_exchange, buy_exchange)]:
                    if prices[buy_ex] and prices[sell_ex]:
                        opportunity = await self.calculate_arbitrage(
                            coin, buy_ex, sell_ex, prices[buy_ex], prices[sell_ex]
                        )
                        
                        if opportunity["net_profit_percent"] > best_profit:
                            best_profit = opportunity["net_profit_percent"]
                            best_opportunity = opportunity
        
        return best_opportunity or {
            "coin": coin,
            "net_profit_percent": 0,
            "is_profitable": False,
            "message": "Не знайдено прибуткових можливостей"
        }

    async def calculate_arbitrage(self, coin: str, buy_exchange: str, 
                                 sell_exchange: str, buy_price: float, 
                                 sell_price: float, amount: float = 1.0) -> Dict:
        """
        Розрахунок арбітражу для конкретної пари бірж
        """
        # Комісії
        buy_fee_percent = get_trading_fee(buy_exchange, self.fee_mode)
        sell_fee_percent = get_trading_fee(sell_exchange, self.fee_mode)
        
        # Конвертація в десятковий дріб
        buy_fee_decimal = buy_fee_percent / 100
        sell_fee_decimal = sell_fee_percent / 100
        
        # Комісії на вивід
        withdrawal_fee_buy = get_withdrawal_fee(coin, buy_exchange)
        withdrawal_fee_sell = get_withdrawal_fee(coin, sell_exchange)
        
        # Розрахунок P&L
        buy_cost = buy_price * amount * (1 + buy_fee_decimal)
        sell_revenue = sell_price * amount * (1 - sell_fee_decimal)
        
        # Вивід
        withdrawal_fee_usd = (withdrawal_fee_buy + withdrawal_fee_sell) * buy_price
        
        net_profit = sell_revenue - buy_cost - withdrawal_fee_usd
        net_profit_percent = (net_profit / buy_cost) * 100 if buy_cost > 0 else 0
        
        # Оцінка ризиків
        buy_liquidity = self.get_liquidity_score(buy_exchange, coin)
        sell_liquidity = self.get_liquidity_score(sell_exchange, coin)
        avg_liquidity = (buy_liquidity + sell_liquidity) / 2
        
        risk_level = self._calculate_risk_level(avg_liquidity, net_profit_percent)
        min_profit_threshold = self._get_min_profit_threshold(risk_level)
        is_profitable = net_profit_percent > min_profit_threshold
        
        return {
            "coin": coin,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "buy_price": round(buy_price, 4),
            "sell_price": round(sell_price, 4),
            "price_difference_percent": round(((sell_price - buy_price) / buy_price) * 100, 4),
            "net_profit_percent": round(net_profit_percent, 4),
            "net_profit_usd": round(net_profit, 2),
            "is_profitable": is_profitable,
            "risk_level": risk_level,
            "liquidity_score": round(avg_liquidity, 2),
            "fee_mode": self.fee_mode,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_liquidity_score(self, exchange: str, coin: str) -> float:
        """Отримати оцінку ліквідності"""
        return self.liquidity_scores.get(exchange, {}).get(coin, 0.5)

    def _calculate_risk_level(self, liquidity_score: float, profit_percent: float) -> str:
        """Розрахувати рівень ризику"""
        if liquidity_score > 0.85 and profit_percent > 0.5:
            return "LOW"
        elif liquidity_score > 0.7 and profit_percent > 0.3:
            return "MEDIUM"
        elif liquidity_score > 0.5 and profit_percent > 0.2:
            return "MEDIUM_HIGH"
        else:
            return "HIGH"

    def _get_min_profit_threshold(self, risk_level: str) -> float:
        """Мінімальний поріг прибутковості"""
        thresholds = {
            "LOW": 0.1,
            "MEDIUM": 0.2,
            "MEDIUM_HIGH": 0.3,
            "HIGH": 0.5
        }
        return thresholds.get(risk_level, 0.3)

    def _filter_profitable_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Фільтр прибуткових можливостей"""
        return [opp for opp in opportunities if opp.get("is_profitable", False)]

    def _error_response(self, message: str) -> Dict:
        """Відповідь з помилкою"""
        return {
            "error": message,
            "success": False,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ==================== УТИЛІТИ ====================

    def add_coin(self, coin: str, symbols: Dict[str, str]):
        """
        Додати нову монету
        symbols: {"Binance": "BTCUSDT", "Kraken": "XXBTZUSD", ...}
        """
        self.symbol_map[coin] = symbols
        self.supported_coins.append(coin)
        
        # Додати оцінки ліквідності
        for exchange in self.supported_exchanges:
            if exchange not in self.liquidity_scores:
                self.liquidity_scores[exchange] = {}
            self.liquidity_scores[exchange][coin] = 0.7
        
        print(f"Додано монету {coin}")

    def add_exchange(self, name: str, client):
        """Додати нову біржу"""
        self.exchanges[name] = client
        self.supported_exchanges.append(name)
        print(f"Додано біржу {name}")

    def get_stats(self) -> Dict:
        """Статистика системи"""
        return {
            "supported_coins": len(self.supported_coins),
            "supported_exchanges": len(self.supported_exchanges),
            "total_pairs": len(self.supported_coins) * len(self.supported_exchanges) * (len(self.supported_exchanges) - 1),
            "coins": self.supported_coins,
            "exchanges": self.supported_exchanges
        }

# ==================== КЛІЄНТИ ДЛЯ НОВИХ БІРЖ ====================

class CoinbaseClient:
    """Клієнт для Coinbase API"""
    async def get_price(self, symbol: str) -> Dict:
        # TODO: Реалізувати реальний API
        return {"price": 0.0, "exchange": "Coinbase"}

class BybitClient:
    """Клієнт для Bybit API"""
    async def get_price(self, symbol: str) -> Dict:
        # TODO: Реалізувати реальний API
        return {"price": 0.0, "exchange": "Bybit"}

class OKXClient:
    """Клієнт для OKX API"""
    async def get_price(self, symbol: str) -> Dict:
        # TODO: Реалізувати реальний API
        return {"price": 0.0, "exchange": "OKX"}