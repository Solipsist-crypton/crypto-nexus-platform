from pydantic import BaseModel
from typing import Any, Optional

class ArbitrageResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    count: int = 0
    message: str = ""