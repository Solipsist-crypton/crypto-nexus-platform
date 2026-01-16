"""
Гнучка конфігурація комісій бірж
Легко змінювати для тестування різних сценаріїв
"""

# ============ БАЗОВІ НАЛАШТУВАННЯ КОМІСІЙ ============

# Режим: 'conservative' (з високими комісіями) або 'optimistic' (з низькими)
FEE_MODE = "conservative"

# БАЗОВІ КОМІСІЇ (можна легко змінювати)
BASE_FEES = {
    "conservative": {
        # Консервативний підхід (високі комісії)
        "Binance": {
            "maker": 0.0010,  # 0.10%
            "taker": 0.0010,  # 0.10%
            "withdrawal_multiplier": 1.0  # Множник комісії виводу
        },
        "Kraken": {
            "maker": 0.0016,  # 0.16%
            "taker": 0.0026,  # 0.26%
            "withdrawal_multiplier": 1.0
        }
    },
    "optimistic": {
        # Оптимістичний підхід (нижчі комісії)
        "Binance": {
            "maker": 0.0008,  # 0.08% (з урахуванням BNB знижки)
            "taker": 0.0008,  # 0.08%
            "withdrawal_multiplier": 0.8
        },
        "Kraken": {
            "maker": 0.0012,  # 0.12% (знижений рівень)
            "taker": 0.0020,  # 0.20%
            "withdrawal_multiplier": 0.8
        }
    }
}

# ============ КОМІСІЇ НА ВИВІД (ФІКСОВАНІ) ============
# Це реальні фіксовані комісії бірж

WITHDRAWAL_FEES = {
    "BTC": {
        "Binance": 0.0005,  # 0.0005 BTC
        "Kraken": 0.0005,   # 0.0005 BTC
        "min_amount": 0.001  # Мінімальний вивід
    },
    "ETH": {
        "Binance": 0.004,   # 0.004 ETH
        "Kraken": 0.004,    # 0.004 ETH
        "min_amount": 0.01
    },
    "SOL": {
        "Binance": 0.01,    # 0.01 SOL
        "Kraken": 0.01,     # 0.01 SOL
        "min_amount": 0.1
    }
}

# ============ УТИЛІТНІ ФУНКЦІЇ ============

def get_trading_fee(exchange: str, order_type: str = "taker") -> float:
    """
    Отримати торгову комісію для біржі
    
    exchange: "Binance" або "Kraken"
    order_type: "maker" або "taker"
    """
    mode_fees = BASE_FEES.get(FEE_MODE, BASE_FEES["conservative"])
    exchange_fees = mode_fees.get(exchange, {})
    
    if order_type == "maker":
        return exchange_fees.get("maker", 0.0015)  # За замовчуванням 0.15%
    else:
        return exchange_fees.get("taker", 0.0025)  # За замовчуванням 0.25%

def get_withdrawal_fee(coin: str, exchange: str) -> float:
    """
    Отримати комісію на вивід
    
    coin: "BTC", "ETH", "SOL"
    exchange: "Binance" або "Kraken"
    """
    coin_fees = WITHDRAWAL_FEES.get(coin, {})
    base_fee = coin_fees.get(exchange, 0.0)
    
    # Застосувати множник з налаштувань
    mode_fees = BASE_FEES.get(FEE_MODE, BASE_FEES["conservative"])
    multiplier = mode_fees.get(exchange, {}).get("withdrawal_multiplier", 1.0)
    
    return base_fee * multiplier

def set_fee_mode(mode: str):
    """
    Змінити режим комісій
    
    mode: "conservative" або "optimistic"
    """
    global FEE_MODE
    if mode in BASE_FEES:
        FEE_MODE = mode
        print(f"✅ Режим комісій змінено на: {mode}")
    else:
        print(f"❌ Невідомий режим: {mode}. Залишено: {FEE_MODE}")

def update_fee(exchange: str, maker: float = None, taker: float = None):
    """
    Оновити комісії для конкретної біржі
    
    exchange: "Binance" або "Kraken"
    maker: нова maker комісія (опціонально)
    taker: нова taker комісія (опціонально)
    """
    if exchange in BASE_FEES["conservative"]:
        if maker is not None:
            BASE_FEES["conservative"][exchange]["maker"] = maker
            BASE_FEES["optimistic"][exchange]["maker"] = maker * 0.8  # Автоматична знижка для optimistic
        if taker is not None:
            BASE_FEES["conservative"][exchange]["taker"] = taker
            BASE_FEES["optimistic"][exchange]["taker"] = taker * 0.8
            
        print(f"✅ Оновлено комісії для {exchange}: maker={maker or 'не змінено'}, taker={taker or 'не змінено'}")