FEES_CONFIG = {
    'Binance': {'maker': 0.1, 'taker': 0.1},
    'Kraken': {'maker': 0.16, 'taker': 0.26},
    'Coinbase': {'maker': 0.4, 'taker': 0.6},
    'Bybit': {'maker': 0.1, 'taker': 0.1},
    'OKX': {'maker': 0.08, 'taker': 0.1}
}

# Конфігурація для символів
SYMBOL_CONFIG = {
    'BTC': {
        'Binance': 'BTCUSDT',
        'Kraken': 'XXBTZUSD',
        'Coinbase': 'BTC-USD',
        'Bybit': 'BTCUSDT',
        'OKX': 'BTC-USDT'
    },
    'ETH': {
        'Binance': 'ETHUSDT',
        'Kraken': 'XETHZUSD',
        'Coinbase': 'ETH-USD',
        'Bybit': 'ETHUSDT',
        'OKX': 'ETH-USDT'
    },
    # ... інші монети
}