from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Додаємо ці імпорти:
from .database import engine, Base
# ІМПОРТУЄМО МОДЕЛІ
from .models import arbitrage as arbitrage_models
from .api import arbitrage as arbitrage_api

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Створюємо таблиці в базі даних
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crypto Nexus Platform API",
    description="Комплексна платформа для арбітражу, ф'ючерсів та аірдропів",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Реєструємо роутер арбітражу
app.include_router(arbitrage_api.router)

@app.get("/")
async def root():
    return {"message": "Crypto Nexus Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}