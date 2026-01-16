import asyncio
from typing import List, Dict, Optional, Tuple, Any
from app.exchanges.binance_client import BinanceClient
from app.exchanges.kraken_client import KrakenClient
from datetime import datetime
from app.config.fees_config import get_trading_fee, get_withdrawal_fee, set_fee_mode, update_fee

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
        
        # Підтримувані монети
        self.supported_coins = ["BTC", "ETH", "SOL"]
        
        # Режим комісій (за замовчуванням taker)
        self.fee_mode = "taker"
        
        # Налаштування ліквідності (тимчасові значення)
        self.liquidity_scores = {
            "Binance": {"BTC": 0.9, "ETH": 0.85, "SOL": 0.8},
            "Kraken": {"BTC": 0.85, "ETH": 0.8, "SOL": 0.75}
        }

    # ==================== ОСНОВНА ЛОГІКА ====================

    async def calculate_real_arbitrage(self, coin: str, buy_exchange: str, 
                                      sell_exchange: str, amount: float = 1.0) -> Dict:
        """
        Розрахунок реального арбітражу з усіма комісіями
        Повертає детальний аналіз прибутковості
        """
        # Перевірка вхідних параметрів
        if coin not in self.supported_coins:
            return self._error_response(f"Монета {coin} не підтримується")
        
        if buy_exchange not in ["Binance", "Kraken"] or sell_exchange not in ["Binance", "Kraken"]:
            return self._error_response("Непідтримувана біржа")
        
        # Отримати ціни з бірж
        buy_price_data, sell_price_data = await self._fetch_prices_for_exchanges(
            coin, buy_exchange, sell_exchange
        )
        
        if not buy_price_data or not sell_price_data:
            return self._error_response("Не вдалося отримати ціни з бірж")
        
        # Ціни
        buy_price = buy_price_data["price"]
        sell_price = sell_price_data["price"]
        
        # Розрахунок різниці цін
        price_difference = sell_price - buy_price
        price_difference_percent = (price_difference / buy_price) * 100 if buy_price > 0 else 0
        
        # Комісії
        buy_fee_percent = get_trading_fee(buy_exchange, self.fee_mode)
        sell_fee_percent = get_trading_fee(sell_exchange, self.fee_mode)
        
        # Комісії на вивід
        withdrawal_fee_buy = get_withdrawal_fee(coin, buy_exchange)
        withdrawal_fee_sell = get_withdrawal_fee(coin, sell_exchange)
        
        # Розрахунок P&L
        buy_cost = buy_price * amount * (1 + buy_fee_percent/100)
        sell_revenue = sell_price * amount * (1 - sell_fee_percent/100)
        
        # Врахувати вивід (конвертуємо в USD еквівалент)
        withdrawal_fee_usd = (withdrawal_fee_buy + withdrawal_fee_sell) * buy_price
        
        net_profit = sell_revenue - buy_cost - withdrawal_fee_usd
        net_profit_percent = (net_profit / buy_cost) * 100 if buy_cost > 0 else 0
        
        # Оцінка ліквідності та ризиків
        buy_liquidity = self.get_liquidity_score(buy_exchange, coin)
        sell_liquidity = self.get_liquidity_score(sell_exchange, coin)
        avg_liquidity = (buy_liquidity + sell_liquidity) / 2
        
        # Визначення рівня ризику
        risk_level = self._calculate_risk_level(avg_liquidity, net_profit_percent)
        
        # Критерій прибутковості (з урахуванням ризику)
        min_profit_threshold = self._get_min_profit_threshold(risk_level)
        is_profitable = net_profit_percent > min_profit_threshold
        
        # Формуємо відповідь
        return {
            # Основна інформація
            "coin": coin,
            "amount": amount,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "direction": f"{buy_exchange} → {sell_exchange}",
            
            # Ціни
            "buy_price": round(buy_price, 2),
            "sell_price": round(sell_price, 2),
            "price_difference": round(price_difference, 2),
            "price_difference_percent": round(price_difference_percent, 4),
            
            # Комісії
            "buy_fee_percent": round(buy_fee_percent, 3),
            "sell_fee_percent": round(sell_fee_percent, 3),
            "withdrawal_fee_usd": round(withdrawal_fee_usd, 2),
            
            # Прибутковість
            "buy_cost_usd": round(buy_cost, 2),
            "sell_revenue_usd": round(sell_revenue, 2),
            "net_profit_usd": round(net_profit, 2),
            "net_profit_percent": round(net_profit_percent, 4),
            
            # Оцінка ризиків
            "buy_liquidity_score": round(buy_liquidity, 2),
            "sell_liquidity_score": round(sell_liquidity, 2),
            "avg_liquidity_score": round(avg_liquidity, 2),
            "risk_level": risk_level,
            "is_profitable": is_profitable,
            "min_profit_threshold": min_profit_threshold,
            
            # Метадані
            "timestamp": datetime.utcnow().isoformat(),
            "fee_mode": self.fee_mode,
            "success": True
        }

    async def compare_prices(self, coin: str = "BTC") -> Dict:
        """
        Порівняти ціни на Binance та Kraken для однієї монети
        Тепер використовує реальні комісії з fees_config
        """
        if coin not in self.supported_coins:
            return self._error_response(f"Монета {coin} не підтримується")
        
        # Отримання цін
        binance_price, kraken_price = await self._fetch_prices(coin)
        
        if not binance_price or not kraken_price:
            return self._error_response("Не вдалося отримати ціни з бірж")
        
        # Аналіз обох напрямків
        binance_to_kraken = await self.calculate_real_arbitrage(
            coin, "Binance", "Kraken", 1.0
        )
        
        kraken_to_binance = await self.calculate_real_arbitrage(
            coin, "Kraken", "Binance", 1.0
        )
        
        # Визначаємо кращий напрямок
        best_direction = None
        if "net_profit_percent" in binance_to_kraken and "net_profit_percent" in kraken_to_binance:
            if binance_to_kraken["net_profit_percent"] > kraken_to_binance["net_profit_percent"]:
                best_direction = binance_to_kraken
                best_direction["best_direction"] = "Binance → Kraken"
            else:
                best_direction = kraken_to_binance
                best_direction["best_direction"] = "Kraken → Binance"
        
        return {
            "coin": coin,
            "binance_price": round(binance_price.get("price", 0), 2),
            "kraken_price": round(kraken_price.get("price", 0), 2),
            "best_opportunity": best_direction,
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        }

    async def scan_all_coins(self) -> List[Dict]:
        """
        Сканувати всі монети та повертати детальний аналіз
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

    # ==================== ДОПОМІЖНІ МЕТОДИ ====================

    async def _fetch_prices_for_exchanges(self, coin: str, buy_exchange: str, 
                                        sell_exchange: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Отримати ціни для конкретних бірж
        """
        try:
            if buy_exchange == "Binance":
                buy_task = self.binance.get_price(self.symbol_map[coin]["binance"])
            else:
                buy_task = self.kraken.get_price(self.symbol_map[coin]["kraken"])
            
            if sell_exchange == "Binance":
                sell_task = self.binance.get_price(self.symbol_map[coin]["binance"])
            else:
                sell_task = self.kraken.get_price(self.symbol_map[coin]["kraken"])
            
            buy_price, sell_price = await asyncio.gather(buy_task, sell_task)
            return buy_price, sell_price
            
        except Exception as e:
            print(f"Помилка отримання цін для {coin}: {e}")
            return None, None

    async def _fetch_prices(self, coin: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Отримати ціни з Binance та Kraken
        """
        try:
            binance_symbol = self.symbol_map[coin]["binance"]
            kraken_symbol = self.symbol_map[coin]["kraken"]
            
            binance_task = self.binance.get_price(binance_symbol)
            kraken_task = self.kraken.get_price(kraken_symbol)
            
            binance_price, kraken_price = await asyncio.gather(binance_task, kraken_task)
            return binance_price, kraken_price
            
        except Exception as e:
            print(f"Помилка отримання цін для {coin}: {e}")
            return None, None

    def get_liquidity_score(self, exchange: str, coin: str) -> float:
        """
        Отримати оцінку ліквідності
        """
        # Тимчасово повертаємо фіксоване значення
        # TODO: Замінити на реальні дані з API
        return self.liquidity_scores.get(exchange, {}).get(coin, 0.5)

    def _calculate_risk_level(self, liquidity_score: float, profit_percent: float) -> str:
        """
        Розрахувати рівень ризику
        """
        if liquidity_score > 0.8 and profit_percent > 0.5:
            return "LOW"
        elif liquidity_score > 0.6 and profit_percent > 0.3:
            return "MEDIUM"
        elif liquidity_score > 0.4 and profit_percent > 0.2:
            return "MEDIUM_HIGH"
        else:
            return "HIGH"

    def _get_min_profit_threshold(self, risk_level: str) -> float:
        """
        Отримати мінімальний поріг прибутковості за рівнем ризику
        """
        thresholds = {
            "LOW": 0.1,        # 0.1% для низького ризику
            "MEDIUM": 0.2,     # 0.2% для середнього ризику
            "MEDIUM_HIGH": 0.3, # 0.3% для високого середнього ризику
            "HIGH": 0.5        # 0.5% для високого ризику
        }
        return thresholds.get(risk_level, 0.3)

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

    def set_fee_mode(self, mode: str):
        """
        Встановити режим комісій (maker/taker)
        """
        if mode in ["maker", "taker"]:
            self.fee_mode = mode
            print(f"Режим комісій змінено на: {mode}")
            set_fee_mode(mode)  # Оновлюємо глобальний конфіг
        else:
            raise ValueError("Режим комісій повинен бути 'maker' або 'taker'")

    def update_exchange_fee(self, exchange: str, maker_fee: float, taker_fee: float):
        """
        Оновити комісії біржі в конфігурації
        """
        update_fee(exchange, maker_fee, taker_fee)
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
        
        # Додаємо стандартні оцінки ліквідності
        if "Binance" not in self.liquidity_scores:
            self.liquidity_scores["Binance"] = {}
        if "Kraken" not in self.liquidity_scores:
            self.liquidity_scores["Kraken"] = {}
            
        self.liquidity_scores["Binance"][coin] = 0.7
        self.liquidity_scores["Kraken"][coin] = 0.65
        
        print(f"Додано монету {coin}: Binance={binance_symbol}, Kraken={kraken_symbol}")

    def get_supported_coins(self) -> List[str]:
        """
        Отримати список підтримуваних монет
        """
        return self.supported_coins.copy()

    def get_exchange_info(self, exchange: str) -> Dict:
        """
        Отримати інформацію про біржу
        """
        return {
            "fee_mode": self.fee_mode,
            "trading_fee": get_trading_fee(exchange, self.fee_mode),
            "supported_coins": [
                coin for coin in self.supported_coins 
                if coin in self.symbol_map
            ]
        }