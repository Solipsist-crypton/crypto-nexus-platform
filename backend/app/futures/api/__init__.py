from .router import router as futures_router
from .entry_points import router as entry_points_router
from .history import router as history_router  # Додаємо history

# Включіть entry_points_router в futures_router
futures_router.include_router(
    entry_points_router, 
    prefix="/entry-points",
    tags=["entry-points"]
)

# Включіть history_router ОКРЕМО (без подвійного префіксу)
futures_router.include_router(
    history_router,
    prefix="/history",
    tags=["history"]
)

# virtual_trades НЕ включайте - його маршрути вже в router.py