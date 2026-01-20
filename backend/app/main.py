from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Імпортуємо моделі
from .database import engine, Base
from .models import arbitrage as arbitrage_models

# Імпортуємо роутери - ТЕПЕР ТІЛЬКИ arbitrage_api
from .api import arbitrage as arbitrage_api
from .api import binance as binance_api
from .api import kraken as kraken_api
# arbitrage_calc БІЛЬШЕ НЕ ІМПОРТУЄМО!
from app.api.coinbase import router as coinbase_router
from app.api.bybit import router as bybit_router
from app.api.okx import router as okx_router
# 1. ІМПОРТУЙ РОУТЕР (додай цей рядок):
#from app.api.gateio import router as gateio_router  # Заміни gateio на назву біржі
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS налаштування
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Реєстрація роутерів - ТЕПЕР ТІЛЬКИ arbitrage_api
app.include_router(arbitrage_api.router, prefix="/api/arbitrage", tags=["arbitrage"])
app.include_router(binance_api.router, prefix="/api/binance", tags=["binance"])
app.include_router(kraken_api.router, prefix="/api/kraken", tags=["kraken"])
# arbitrage_calc_api.router БІЛЬШЕ НЕ ІСНУЄ - ми його видалили
app.include_router(coinbase_router, prefix="/api/coinbase", tags=["coinbase"])
app.include_router(bybit_router, prefix="/api/bybit", tags=["bybit"])
app.include_router(okx_router, prefix="/api/okx", tags=["okx"])
# 2. ДОДАЙ РОУТЕР ДО APP (додай цей рядок):
#app.include_router(gateio_router, prefix="/api/gateio", tags=["GateIO"])  # Заміни gateio
# Створюємо таблиці в базі даних
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Crypto Nexus Platform API"}

@app.get("/health")
async def health_check():
    from datetime import datetime, timezone
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

try:
    from backend.app.futures.api.router import router as futures_router
    app.include_router(futures_router, prefix="/api/futures", tags=["futures"])
    print("✅ Futures module loaded successfully")
except Exception as e:
    print(f"⚠️  Futures module error: {e}")
    print("⚠️  Continuing without futures module...")