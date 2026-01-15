from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..models.arbitrage import ArbitrageOpportunity as ArbitrageModel

# Схеми Pydantic (без імпорту з schemas для уникнення циклічності)
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

class ArbitrageOpportunityResponse(ArbitrageOpportunityBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/api/arbitrage", tags=["arbitrage"])

@router.get("/opportunities", response_model=List[ArbitrageOpportunityResponse])
def get_opportunities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    min_profit: Optional[float] = Query(1.0, description="Мінімальний прибуток у %"),
    base_currency: Optional[str] = None
):
    """
    Отримати список арбітражних можливостей
    """
    query = db.query(ArbitrageModel).filter(
        ArbitrageModel.price_difference >= min_profit,
        ArbitrageModel.is_opportunity == True
    )
    
    if base_currency:
        query = query.filter(ArbitrageModel.base_currency == base_currency)
    
    return query.offset(skip).limit(limit).all()

@router.post("/opportunities", response_model=ArbitrageOpportunityResponse)
def create_opportunity(
    opportunity: ArbitrageOpportunityCreate,
    db: Session = Depends(get_db)
):
    """
    Додати нову арбітражну можливість
    """
    db_opportunity = ArbitrageModel(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

@router.get("/opportunities/{id}", response_model=ArbitrageOpportunityResponse)
def get_opportunity(id: int, db: Session = Depends(get_db)):
    """
    Отримати конкретну арбітражну можливість за ID
    """
    opportunity = db.query(ArbitrageModel).filter(ArbitrageModel.id == id).first()
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity