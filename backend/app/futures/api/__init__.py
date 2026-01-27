from .router import router as futures_router
from .virtual_trades import router as virtual_trades_router
from .entry_points import router as entry_points_router
from .history import router as history_router

# Включіть entry_points_router в futures_router
futures_router.include_router(
    entry_points_router, 
    prefix="/entry-points",
    tags=["entry-points"]
)

# Тепер всі будуть доступні під /api/futures