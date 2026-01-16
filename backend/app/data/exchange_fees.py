REAL_EXCHANGE_FEES = {
    "Binance": {
        "BTC": {
            "maker_fee": 0.001,      # 0.1%
            "taker_fee": 0.001,      # 0.1%
            "withdrawal_fee": 0.0005, # 0.0005 BTC
            "min_withdrawal": 0.001,
            "daily_volume": 25000000,  # $25M
            "spread": 0.01,           # 0.01%
            "pairs": ["BTCUSDT", "BTCBUSD"]
        },
        "ETH": {
            "maker_fee": 0.001,
            "taker_fee": 0.001,
            "withdrawal_fee": 0.004,
            "min_withdrawal": 0.01,
            "daily_volume": 15000000,
            "spread": 0.02,
            "pairs": ["ETHUSDT", "ETHBUSD"]
        },
        "SOL": {
            "maker_fee": 0.001,
            "taker_fee": 0.001,
            "withdrawal_fee": 0.01,
            "min_withdrawal": 0.1,
            "daily_volume": 8000000,
            "spread": 0.03,
            "pairs": ["SOLUSDT"]
        }
    },
    "Kraken": {
        "BTC": {
            "maker_fee": 0.0016,     # 0.16%
            "taker_fee": 0.0026,     # 0.26%
            "withdrawal_fee": 0.0005,
            "min_withdrawal": 0.001,
            "daily_volume": 18000000,
            "spread": 0.015,
            "pairs": ["XXBTZUSD", "XXBTZEUR"]
        },
        "ETH": {
            "maker_fee": 0.0016,
            "taker_fee": 0.0026,
            "withdrawal_fee": 0.004,
            "min_withdrawal": 0.01,
            "daily_volume": 12000000,
            "spread": 0.025,
            "pairs": ["XETHZUSD", "XETHZEUR"]
        },
        "SOL": {
            "maker_fee": 0.0020,
            "taker_fee": 0.0026,
            "withdrawal_fee": 0.01,
            "min_withdrawal": 0.1,
            "daily_volume": 5000000,
            "spread": 0.035,
            "pairs": ["SOLUSD", "SOLEUR"]
        }
    }
}