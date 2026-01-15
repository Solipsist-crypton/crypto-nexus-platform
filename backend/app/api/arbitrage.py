from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/arbitrage", tags=["arbitrage"])

@router.get("/opportunities", response_model=List[schemas.ArbitrageOpportunity])
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
    query = db.query(models.ArbitrageOpportunity).filter(
        models.ArbitrageOpportunity.price_difference >= min_profit,
        models.ArbitrageOpportunity.is_opportunity == True
    )
    
    if base_currency:
        query = query.filter(models.ArbitrageOpportunity.base_currency == base_currency)
    
    return query.offset(skip).limit(limit).all()

@router.post("/opportunities", response_model=schemas.ArbitrageOpportunity)
def create_opportunity(
    opportunity: schemas.ArbitrageOpportunityCreate,
    db: Session = Depends(get_db)
):
    """
    Додати нову арбітражну можливість
    """
    db_opportunity = models.ArbitrageOpportunity(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

@router.get("/opportunities/{id}", response_model=schemas.ArbitrageOpportunity)
def get_opportunity(id: int, db: Session = Depends(get_db)):
    """
    Отримати конкретну арбітражну можливість за ID
    """
    opportunity = db.query(models.ArbitrageOpportunity).filter(models.ArbitrageOpportunity.id == id).first()
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity