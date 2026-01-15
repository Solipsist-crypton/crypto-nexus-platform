from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArbitrageOpportunityBase(BaseModel):
    base_currency: str
    target_currency: str
    exchange_from: str
    exchange_to: str
    price_from: float
    price_to: float
    price_difference: float
    volume_24h: Optional[float] = None
    trust_score: Optional[float] = None
    potential_profit: Optional[float] = None
    is_opportunity: bool = True

class ArbitrageOpportunityCreate(ArbitrageOpportunityBase):
    pass

class ArbitrageOpportunity(ArbitrageOpportunityBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Замість orm_mode для Pydantic v2