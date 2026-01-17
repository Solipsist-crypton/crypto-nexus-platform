import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

# Імпорти клієнтів бірж
from app.api.binance import BinanceClient
from app.api.kraken import KrakenClient
from app.api.coinbase import CoinbaseClient
from app.api.bybit import BybitClient
from app.api.okx import OKXClient

# Для FEES_CONFIG
try:
    from app.config.settings import FEES_CONFIG
except ImportError:
    FEES_CONFIG = {
        'Binance': {'maker': 0.1, 'taker': 0.1},
        'Kraken': {'maker': 0.16, 'taker': 0.26},
        'Coinbase': {'maker': 0.4, 'taker': 0.6},
        'Bybit': {'maker': 0.1, 'taker': 0.1},
        'OKX': {'maker': 0.08, 'taker': 0.1}
    }
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ FEES_CONFIG не знайдено, використовуються стандартні значення")

logger = logging.getLogger(__name__)


class ArbitrageCalculator:
    def __init__(self, threshold: float = 0.1, excluded_coins: Optional[List[str]] = None):
        self.threshold = threshold
        self.excluded_coins = excluded_coins or []
        
        # Біржі, які ТИМЧАСОВО виключаємо (Coinbase не працює)
        self.excluded_exchanges = ['Coinbase']
        
        # Ініціалізація клієнтів
        self.exchange_clients = {
            'Binance': BinanceClient(),
            'Kraken': KrakenClient(),
            'Coinbase': CoinbaseClient(),  # Залишаємо, але не використовуватимемо
            'Bybit': BybitClient(),
            'OKX': OKXClient()
        }
        
        # Символи для бірж
        self.exchange_symbols = {
            'BTC': {'Binance': 'BTCUSDT', 'Kraken': 'XXBTZUSD', 'Coinbase': 'BTC-USD', 'Bybit': 'BTCUSDT', 'OKX': 'BTC-USDT'},
            'ETH': {'Binance': 'ETHUSDT', 'Kraken': 'XETHZUSD', 'Coinbase': 'ETH-USD', 'Bybit': 'ETHUSDT', 'OKX': 'ETH-USDT'},
            'XRP': {'Binance': 'XRPUSDT', 'Kraken': 'XXRPZUSD', 'Coinbase': 'XRP-USD', 'Bybit': 'XRPUSDT', 'OKX': 'XRP-USDT'},
            'ADA': {'Binance': 'ADAUSDT', 'Kraken': 'ADAUSD', 'Coinbase': 'ADA-USD', 'Bybit': 'ADAUSDT', 'OKX': 'ADA-USDT'},
            'DOT': {'Binance': 'DOTUSDT', 'Kraken': 'DOTUSD', 'Coinbase': 'DOT-USD', 'Bybit': 'DOTUSDT', 'OKX': 'DOT-USDT'},
            'DOGE': {'Binance': 'DOGEUSDT', 'Kraken': 'XDGUSD', 'Coinbase': 'DOGE-USD', 'Bybit': 'DOGEUSDT', 'OKX': 'DOGE-USDT'},
            'AVAX': {'Binance': 'AVAXUSDT', 'Kraken': 'AVAXUSD', 'Coinbase': 'AVAX-USD', 'Bybit': 'AVAXUSDT', 'OKX': 'AVAX-USDT'},
            'MATIC': {'Binance': 'MATICUSDT', 'Kraken': 'MATICUSD', 'Coinbase': 'MATIC-USD', 'Bybit': 'MATICUSDT', 'OKX': 'MATIC-USDT'}
        }

    async def _get_price_from_exchange(self, exchange: str, symbol: str) -> Optional[float]:
        """Отримати ціну з конкретної біржі (спрощено)"""
        try:
            # Пропускаємо виключені біржі
            if exchange in self.excluded_exchanges:
                logger.debug(f"⏭️ Пропускаємо виключену біржу: {exchange}")
                return None
            
            if exchange not in self.exchange_clients:
                logger.warning(f"⚠️ Біржа {exchange} не підтримується")
                return None
            
            client = self.exchange_clients[exchange]
            logger.info(f"      → Виклик client.get_price('{symbol}')...")
            
            price_data = await client.get_price(symbol)
            
            if price_data and 'price' in price_data:
                price = float(price_data['price'])
                
                # ПРОСТА ПЕРЕВІРКА: ціна має бути > 0
                if price <= 0:
                    logger.warning(f"⚠️ {exchange}: Недійсна ціна {price} для {symbol}")
                    return None
                
                logger.info(f"      → Отримано: {price_data}")
                return price
            else:
                logger.warning(f"⚠️ {exchange}: price_data = None або пустий")
                return None
                
        except Exception as e:
            logger.error(f"❌ Помилка отримання ціни з {exchange} для {symbol}: {e}")
            return None

    async def _get_prices_for_coin(self, coin: str) -> Dict[str, Optional[float]]:
        """Отримати ціни для монети з усіх бірж (крім виключених)"""
        logger.info(f"🔍 Отримання цін для {coin} (без {self.excluded_exchanges})")
        
        if coin not in self.exchange_symbols:
            logger.error(f"❌ Монета {coin} не підтримується")
            return {}
        
        symbols = self.exchange_symbols[coin]
        prices = {}
        
        # ДОДАЄМО ДЕТАЛЬНЕ ЛОГУВАННЯ
        logger.info(f"📋 Символи для {coin}: {symbols}")
        
        # Отримуємо ціни тільки з доступних бірж
        for exchange, symbol in symbols.items():
            # Пропускаємо виключені біржі
            if exchange in self.excluded_exchanges:
                logger.info(f"   ⏭️ Пропускаємо виключену біржу: {exchange}")
                continue
                
            logger.info(f"   🔍 Запит до {exchange} з символом {symbol}")
            price = await self._get_price_from_exchange(exchange, symbol)
            prices[exchange] = price
            
            if price:
                logger.info(f"      ✅ {exchange}: Ціна = {price}")
            else:
                logger.warning(f"      ❌ {exchange}: не вдалося отримати ціну")
        
        logger.info(f"📊 Отримані ціни для {coin}: {prices}")
        
        # РАХУЄМО СКІЛЬКИ УСПІШНИХ
        successful = sum(1 for price in prices.values() if price is not None)
        logger.info(f"📈 Успішних запитів для {coin}: {successful}/{len(prices)}")
        
        return prices

    async def calculate_arbitrage_for_coin(self, coin: str) -> Optional[Dict[str, Any]]:
        """Розрахувати арбітражні можливості для конкретної монети"""
        try:
            # Отримуємо ціни
            prices = await self._get_prices_for_coin(coin)
            
            if not prices:
                logger.warning(f"⚠️ Не вдалося отримати ціни для {coin}")
                return {
                    'coin': coin,
                    'prices': {},
                    'best_opportunity': None,
                    'all_opportunities': [],
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'message': f'Не вдалося отримати ціни для {coin}'
                }
            
            # Фільтруємо тільки дійсні ціни
            valid_prices = {ex: price for ex, price in prices.items() if price is not None}
            
            if len(valid_prices) < 2:
                logger.info(f"📊 {coin}: Недостатньо даних для арбітражу (тільки {len(valid_prices)} бірж)")
                # ВАЖЛИВО: Повертаємо дані навіть якщо немає арбітражу!
                return {
                    'coin': coin,
                    'prices': valid_prices,  # ← ЦЕ ГАРНА ІНФОРМАЦІЯ
                    'best_opportunity': None,
                    'all_opportunities': [],
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'message': f'Недостатньо даних для арбітражу ({len(valid_prices)} бірж)'
                }
            
            # Знаходимо всі можливі пари бірж
            all_opportunities = []
            exchanges = list(valid_prices.keys())
            
            for i in range(len(exchanges)):
                for j in range(len(exchanges)):
                    if i != j:
                        buy_exchange = exchanges[i]
                        sell_exchange = exchanges[j]
                        buy_price = valid_prices[buy_exchange]
                        sell_price = valid_prices[sell_exchange]
                        
                        if buy_price > 0 and sell_price > 0:
                            price_difference = sell_price - buy_price
                            price_difference_percent = (price_difference / buy_price) * 100
                            
                            # Розраховуємо прибуток з урахуванням комісій
                            buy_fee = FEES_CONFIG.get(buy_exchange, {}).get('maker', 0.1) / 100
                            sell_fee = FEES_CONFIG.get(sell_exchange, {}).get('taker', 0.2) / 100
                            
                            net_profit_percent = price_difference_percent - buy_fee - sell_fee
                            
                            # Додаємо можливість тільки якщо прибуток більше порога
                            if net_profit_percent > self.threshold:
                                opportunity = {
                                    'coin': coin,
                                    'buy_exchange': buy_exchange,
                                    'sell_exchange': sell_exchange,
                                    'buy_price': buy_price,
                                    'sell_price': sell_price,
                                    'price_difference': price_difference,
                                    'price_difference_percent': price_difference_percent,
                                    'net_profit_percent': net_profit_percent,
                                    'buy_fee_percent': buy_fee * 100,
                                    'sell_fee_percent': sell_fee * 100,
                                    'timestamp': datetime.now(timezone.utc).isoformat()
                                }
                                all_opportunities.append(opportunity)
            
            if not all_opportunities:
                logger.info(f"📊 {coin}: Немає можливостей з різницею вище {self.threshold}%")
                # ВАЖЛИВО: Повертаємо ціни навіть якщо немає арбітражу!
                return {
                    'coin': coin,
                    'prices': valid_prices,  # ← ОСЬ ТУТ БУЛА ПОМИЛКА!
                    'best_opportunity': None,
                    'all_opportunities': [],
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'message': f'Немає арбітражних можливостей з різницею вище {self.threshold}%'
                }
            
            # Сортуємо за прибутком
            all_opportunities.sort(key=lambda x: x['net_profit_percent'], reverse=True)
            best_opportunity = all_opportunities[0]
            
            logger.info(f"✅ {coin}: Найкраща можливість {best_opportunity['buy_exchange']} → "
                       f"{best_opportunity['sell_exchange']} | "
                       f"Прибуток: {best_opportunity['net_profit_percent']:.2f}%")
            
            return {
                'coin': coin,
                'prices': valid_prices,
                'best_opportunity': best_opportunity,
                'all_opportunities': all_opportunities,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Помилка при розрахунку арбітражу для {coin}: {e}")
            # Навіть при помилці повертаємо структуру
            return {
                'coin': coin,
                'prices': {},
                'best_opportunity': None,
                'all_opportunities': [],
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            }

    async def calculate_arbitrage_all_coins(self) -> List[Dict[str, Any]]:
        """Розрахувати арбітражні можливості для всіх монет"""
        logger.info(f"🔄 Сканування всіх монет (поріг: {self.threshold}%, без бірж: {self.excluded_exchanges})")
        
        results = []
        coins = [coin for coin in self.exchange_symbols.keys() 
                if coin not in self.excluded_coins]
        
        coins = coins[:8]  # Обмеження для тесту
        
        for coin in coins:
            try:
                result = await self.calculate_arbitrage_for_coin(coin)
                if result:
                    results.append(result)
                else:
                    results.append({
                        'coin': coin,
                        'prices': {},
                        'best_opportunity': None,
                        'all_opportunities': [],
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'message': f'Не вдалося розрахувати арбітраж для {coin}'
                    })
                    
            except Exception as e:
                logger.error(f"❌ Помилка для монети {coin}: {e}")
                results.append({
                    'coin': coin,
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        
        # Рахуємо монети з можливостями
        coins_with_opportunities = [r for r in results if r.get('best_opportunity')]
        logger.info(f"✅ Завершено. Знайдено {len(coins_with_opportunities)} монет з можливостями")
        
        return results

    async def find_best_opportunity(self) -> Optional[Dict[str, Any]]:
        """Знайти найкращу арбітражну можливість"""
        logger.info(f"🔍 Пошук найкращої можливості (поріг: {self.threshold}%)")
        
        try:
            all_coin_data = await self.calculate_arbitrage_all_coins()
            
            if not all_coin_data:
                return None
            
            # Збираємо всі кращі можливості
            best_opportunities = []
            for coin_data in all_coin_data:
                best_opp = coin_data.get('best_opportunity')
                if best_opp and best_opp.get('net_profit_percent', 0) > self.threshold:
                    best_opportunities.append(best_opp)
            
            if not best_opportunities:
                logger.info("ℹ️ Не знайдено можливостей з прибутком вище порога")
                return None
            
            # Знаходимо абсолютно найкращу
            absolute_best = max(best_opportunities, 
                              key=lambda x: x.get('net_profit_percent', 0))
            
            logger.info(f"🎯 Найкраща можливість: {absolute_best['coin']} "
                       f"({absolute_best['buy_exchange']} → {absolute_best['sell_exchange']}) "
                       f"| Прибуток: {absolute_best['net_profit_percent']:.2f}%")
            
            return absolute_best
            
        except Exception as e:
            logger.error(f"❌ Помилка при пошуку найкращої можливості: {e}")
            return None

    async def calculate_specific_arbitrage(self, coin: str, buy_exchange: str, 
                                         sell_exchange: str, amount: float = 1.0) -> Dict[str, Any]:
        """Розрахувати конкретну арбітражну операцію"""
        try:
            logger.info(f"🧮 Розрахунок арбітражу: {coin} {buy_exchange} → {sell_exchange}")
            
            # Перевіряємо, чи біржі не виключені
            if buy_exchange in self.excluded_exchanges or sell_exchange in self.excluded_exchanges:
                return {
                    'success': False,
                    'error': f'Одна з бірж виключена з розрахунків: {self.excluded_exchanges}',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Отримуємо ціни
            prices = await self._get_prices_for_coin(coin)
            
            if not prices:
                return {
                    'success': False,
                    'error': f'Не вдалося отримати ціни для {coin}',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            buy_price = prices.get(buy_exchange)
            sell_price = prices.get(sell_exchange)
            
            if not buy_price or not sell_price:
                return {
                    'success': False,
                    'error': f'Не вдалося отримати ціни з вказаних бірж',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Розрахунок різниці
            price_difference = sell_price - buy_price
            price_difference_percent = (price_difference / buy_price) * 100
            
            # Розрахунок з комісіями
            buy_fee = FEES_CONFIG.get(buy_exchange, {}).get('maker', 0.1) / 100
            sell_fee = FEES_CONFIG.get(sell_exchange, {}).get('taker', 0.2) / 100
            
            # Суми
            buy_cost = amount * buy_price * (1 + buy_fee)
            sell_revenue = amount * sell_price * (1 - sell_fee)
            net_profit = sell_revenue - buy_cost
            net_profit_percent = (net_profit / buy_cost) * 100
            
            return {
                'success': True,
                'coin': coin,
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'amount': amount,
                'price_difference': price_difference,
                'price_difference_percent': price_difference_percent,
                'buy_cost': buy_cost,
                'sell_revenue': sell_revenue,
                'net_profit': net_profit,
                'net_profit_percent': net_profit_percent,
                'buy_fee_percent': buy_fee * 100,
                'sell_fee_percent': sell_fee * 100,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': f'Арбітраж розраховано. Прибуток: {net_profit:.2f} ({net_profit_percent:.2f}%)'
            }
            
        except Exception as e:
            logger.error(f"❌ Помилка при розрахунку арбітражу: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }