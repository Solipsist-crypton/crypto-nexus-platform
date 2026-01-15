from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Налаштування бази даних
    DATABASE_URL: str = "postgresql://crypto_user:crypto_pass@localhost:5432/crypto_nexus"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CoinGecko API
    COINGECKO_API_KEY: Optional[str] = None
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_RATE_LIMIT: int = 30  # запитів на хвилину
    
    # Арбітражні налаштування
    MIN_PROFIT_PERCENT: float = 0.3
    MIN_LIQUIDITY_USD: float = 10000.0
    UPDATE_INTERVAL_SECONDS: int = 30
    
    # Сесії та безпека
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()