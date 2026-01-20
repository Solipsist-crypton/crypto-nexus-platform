#!/usr/bin/env python3
"""
Arbitrage Monitor - Фінальна версія (працює з /compare/{coin})
Запуск: python monitor.py
"""
import sqlite3
import requests
import time
import yaml
import os
from datetime import datetime
from tabulate import tabulate
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class SmartArbitrageMonitor:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.db = sqlite3.connect('arb_monitor.db', check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self._create_tables()
        
        # Статистика
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'errors': 0,
            'last_update': None,
            'execution_time': 0
        }
        
        # Кеш бірж
        self.all_exchanges = set()
        
        print("🚀 Smart Arbitrage Monitor ініціалізовано")
        print(f"📡 База URL: {self.config['main_backend']['base_url']}")
        print(f"💰 Монети для моніторингу: {', '.join(self.config['monitor_coins'])}")
        print("="*80)
    
    def _load_config(self, path: str) -> Dict:
        """Завантаження конфігурації"""
        if not os.path.exists(path):
            self._create_default_config(path)
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_default_config(self, path: str):
        """Створення конфігурації за замовчуванням"""
        default_config = {
            'main_backend': {
                'base_url': 'http://localhost:5000',
                'endpoints': {
                    'arbitrage_compare': '/api/arbitrage/compare/{coin}'
                }
            },
            'update_interval': 15,  # 15 секунд - швидко для тесту
            'monitor_coins': ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'AVAX', 'MATIC', 'BNB'],
            'request_timeout': 5,
            'max_workers': 3,  # Паралельні запити
            'min_spread_to_show': 0.1  # Мінімальний спред для виділення
        }
        
        with open(path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ Створено конфігурацію: {path}")
    
    def _create_tables(self):
        """Створення таблиць бази даних"""
        cursor = self.db.cursor()
        
        # Таблиця цін
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                coin TEXT NOT NULL,
                exchange TEXT NOT NULL,
                price REAL NOT NULL,
                UNIQUE(coin, exchange, timestamp)
            )
        ''')
        
        # Таблиця арбітражних угод
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arb_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                coin TEXT NOT NULL,
                buy_exchange TEXT NOT NULL,
                sell_exchange TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                spread_usd REAL NOT NULL,
                spread_percent REAL NOT NULL,
                net_profit_percent REAL NOT NULL
            )
        ''')
        
        # Індекси
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cp_coin ON coin_prices(coin)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cp_time ON coin_prices(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ao_coin_time ON arb_opportunities(coin, timestamp)')
        
        self.db.commit()
    
    def fetch_coin_data(self, coin: str) -> Optional[Dict]:
        """Отримання даних для конкретної монети"""
        base_url = self.config['main_backend']['base_url']
        endpoint = self.config['main_backend']['endpoints']['arbitrage_compare']
        url = f"{base_url}{endpoint.format(coin=coin)}"
        
        try:
            response = requests.get(
                url, 
                timeout=self.config['request_timeout']
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('success') and 'data' in data:
                self.stats['successful_requests'] += 1
                return data['data']
            else:
                print(f"⚠️  {coin}: {data.get('message', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {coin}: Помилка запиту - {type(e).__name__}")
        except Exception as e:
            print(f"❌ {coin}: Неочікувана помилка - {e}")
        
        self.stats['errors'] += 1
        return None
    
    def fetch_all_coins_parallel(self) -> Dict[str, Any]:
        """Паралельне отримання даних для всіх монет"""
        coin_data = {}
        start_time = time.time()
        
        print(f"\n🔄 Оновлення даних для {len(self.config['monitor_coins'])} монет...")
        
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            future_to_coin = {
                executor.submit(self.fetch_coin_data, coin): coin 
                for coin in self.config['monitor_coins']
            }
            
            for future in as_completed(future_to_coin):
                coin = future_to_coin[future]
                try:
                    data = future.result()
                    if data:
                        coin_data[coin] = data
                        
                        # Оновлюємо список бірж
                        if 'prices' in data:
                            self.all_exchanges.update(data['prices'].keys())
                except Exception as e:
                    print(f"❌ {coin}: Помилка обробки - {e}")
        
        self.stats['execution_time'] = time.time() - start_time
        self.stats['total_requests'] = len(self.config['monitor_coins'])
        self.stats['last_update'] = datetime.now()
        
        return coin_data
    
    def save_to_database(self, coin_data: Dict[str, Any]):
        """Збереження даних в SQLite"""
        cursor = self.db.cursor()
        
        for coin, data in coin_data.items():
            # Зберігаємо ціни
            if 'prices' in data:
                timestamp = data.get('timestamp', datetime.now().isoformat())
                for exchange, price in data['prices'].items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO coin_prices 
                        (coin, exchange, price, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (coin, exchange, price, timestamp))
            
            # Зберігаємо найкращу арбітражну угоду
            if 'best_opportunity' in data and data['best_opportunity']:
                opp = data['best_opportunity']
                cursor.execute('''
                    INSERT INTO arb_opportunities 
                    (coin, buy_exchange, sell_exchange, buy_price, sell_price, 
                     spread_usd, spread_percent, net_profit_percent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    coin,
                    opp['buy_exchange'],
                    opp['sell_exchange'],
                    opp['buy_price'],
                    opp['sell_price'],
                    opp['price_difference'],
                    opp['price_difference_percent'],
                    opp['net_profit_percent']
                ))
        
        self.db.commit()
    
    def generate_display_table(self, coin_data: Dict[str, Any]) -> tuple:
        """Генерація таблиці для відображення"""
        if not coin_data:
            return [], [], {}
        
        # Сортуємо біржі алфавітно
        exchanges = sorted(self.all_exchanges)
        
        # Заголовки таблиці
        headers = ['Монета'] + exchanges + ['Найкраща ціна', 'Спред (Max)', 'Прибуток%']
        
        # Дані таблиці
        table_data = []
        stats = {
            'total_coins': len(coin_data),
            'coins_with_arbitrage': 0,
            'max_spread': {'value': 0, 'coin': '', 'pair': ''},
            'total_opportunities': 0
        }
        
        for coin in sorted(coin_data.keys()):
            data = coin_data[coin]
            row = [coin]
            
            # Ціни по біржам
            prices = data.get('prices', {})
            for exchange in exchanges:
                price = prices.get(exchange)
                if price is not None:
                    # Форматування залежно від величини ціни
                    if price >= 1000:
                        row.append(f"${price:,.0f}")
                    elif price >= 1:
                        row.append(f"${price:,.2f}")
                    else:
                        row.append(f"${price:.4f}")
                else:
                    row.append('—')
            
            # Найкраща ціна та арбітраж
            if prices:
                price_values = [p for p in prices.values() if p is not None]
                if price_values:
                    best_price = max(price_values)
                    worst_price = min(price_values)
                    
                    # Найкраща ціна
                    if best_price >= 1000:
                        row.append(f"${best_price:,.0f}")
                    elif best_price >= 1:
                        row.append(f"${best_price:,.2f}")
                    else:
                        row.append(f"${best_price:.4f}")
                    
                    # Спред
                    if len(price_values) > 1:
                        spread_percent = ((best_price - worst_price) / worst_price) * 100
                        
                        # Знаходимо пару бірж
                        best_exchange = [k for k, v in prices.items() if v == best_price][0]
                        worst_exchange = [k for k, v in prices.items() if v == worst_price][0]
                        
                        if spread_percent >= self.config['min_spread_to_show']:
                            row.append(f"{spread_percent:.3f}%")  # Тільки відсоток
                            
                            # Оновлюємо статистику
                            stats['coins_with_arbitrage'] += 1
                            if spread_percent > stats['max_spread']['value']:
                                stats['max_spread'] = {
                                    'value': spread_percent,
                                    'coin': coin,
                                    'pair': f"{worst_exchange}→{best_exchange}"
                                }
                        else:
                            row.append(f"{spread_percent:.3f}%")
                    else:
                        row.append("0.000%")
                else:
                    row.extend(['—', '—'])
            else:
                row.extend(['—', '—'])
            
            # Прибуток з найкращої угоди
            best_opp = data.get('best_opportunity')
            if best_opp and best_opp.get('net_profit_percent', 0) > 0:
                profit = best_opp['net_profit_percent']
                row.append(f"{profit:.3f}%")
                stats['total_opportunities'] += 1
            else:
                row.append('—')
            
            table_data.append(row)
        
        return headers, table_data, stats
    
    def display_results(self, headers: List, table_data: List, stats: Dict):
        """Відображення результатів в консолі"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_duration = f"{self.stats['execution_time']:.1f}s"
        
        print("\n" + "="*100)
        print(f"💰 ARBITRAGE MONITOR | Оновлено: {current_time} ({update_duration})")
        print("="*100)
        
        if table_data:
            # Відображення таблиці
            print(tabulate(
                table_data, 
                headers=headers, 
                tablefmt="simple",  # "simple", "grid", "plain"
                numalign="right",
                stralign="center"
            ))
        else:
            print("📭 Немає даних для відображення")
        
        # Статистика
        print("\n" + "-"*100)
        print("📊 СТАТИСТИКА:")
        print(f"   • Монети: {stats['total_coins']} з {len(self.config['monitor_coins'])}")
        print(f"   • Запити: {self.stats['successful_requests']}/{self.stats['total_requests']} успішних")
        print(f"   • Помилки: {self.stats['errors']}")
        
        if stats['coins_with_arbitrage'] > 0:
            print(f"   • Арбітраж: {stats['coins_with_arbitrage']} монет з можливостями")
            print(f"   • Найкращий спред: {stats['max_spread']['value']:.3f}% "
                  f"({stats['max_spread']['coin']} {stats['max_spread']['pair']})")
            print(f"   • Угоди: {stats['total_opportunities']} з прибутком")
        
        # Попередження
        if self.stats['errors'] > len(self.config['monitor_coins']) / 2:
            print(f"\n⚠️  УВАГА: Багато помилок запитів ({self.stats['errors']})")
            print("   Перевірте: 1) Чи працює бекенд (docker-compose ps)")
            print("              2) Чи відкрито порт 5000")
        
        print("-"*100)
        print(f"🔧 Наступне оновлення через {self.config['update_interval']} сек (Ctrl+C для виходу)")
        print("="*100)
    
    def run_continuous_monitoring(self):
        """Безперервний моніторинг"""
        print("🚀 Запуск безперервного моніторингу...")
        print("   База даних: arb_monitor.db")
        print("   Конфігурація: config.yaml")
        print("="*80)
        
        try:
            while True:
                # 1. Отримуємо дані
                coin_data = self.fetch_all_coins_parallel()
                
                if coin_data:
                    # 2. Зберігаємо в БД
                    self.save_to_database(coin_data)
                    
                    # 3. Генеруємо таблицю
                    headers, table_data, stats = self.generate_display_table(coin_data)
                    
                    # 4. Відображаємо
                    self.display_results(headers, table_data, stats)
                else:
                    print("❌ Не вдалося отримати дані. Перевірте підключення.")
                
                # 5. Чекаємо перед наступним оновленням
                print(f"\n⏳ Очікування {self.config['update_interval']} секунд...", end="")
                for i in range(self.config['update_interval']):
                    print(f"\r⏳ Очікування {self.config['update_interval'] - i} секунд...", end="")
                    time.sleep(1)
                print()
                
        except KeyboardInterrupt:
            self._shutdown()
    
    def _shutdown(self):
        """Коректне завершення роботи"""
        print("\n\n🛑 Зупинка моніторингу...")
        print("📊 Фінальна статистика:")
        print(f"   • Всього запитів: {self.stats['total_requests']}")
        print(f"   • Успішних: {self.stats['successful_requests']}")
        print(f"   • Помилок: {self.stats['errors']}")
        print(f"   • Час виконання: {self.stats.get('execution_time', 0):.1f} сек")
        
        # Показуємо приклади SQL запитів
        print("\n💡 ПРИКЛАДИ SQL-ЗАПИТІВ ДЛЯ АНАЛІЗУ:")
        print("   sqlite3 arb_monitor.db")
        print("   .mode box")
        print("   SELECT * FROM coin_prices WHERE coin='BTC' ORDER BY timestamp DESC LIMIT 5;")
        print("   SELECT coin, MAX(spread_percent) as max_spread FROM arb_opportunities GROUP BY coin;")
        
        self.db.close()
        print("\n✅ Моніторинг зупинено. База даних збережена.")
        print("👋 Гарного дня!")

if __name__ == "__main__":
    monitor = SmartArbitrageMonitor()
    monitor.run_continuous_monitoring()