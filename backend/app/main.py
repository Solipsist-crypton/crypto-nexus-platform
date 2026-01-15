from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .core.config import settings

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Створення додатку
app = FastAPI(
    title="Crypto Nexus Platform API",
    description="Комплексна платформа для арбітражу, ф'ючерсів та аірдропів",
    version="1.0.0"
)

# CORS налаштування
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Crypto Nexus Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"  # Буде замінено на реальний час
    }

@app.get("/api/version")
async def get_version():
    return {
        "backend": "1.0.0",
        "modules": {
            "arbitrage": "active",
            "futures": "planned",
            "airdrops": "planned"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )