from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import random
from typing import List, Optional
from sqlalchemy.orm import Session

# ВІДНОСНІ ІМПОРТИ (правильні для структури)
from app.database import get_db
from app.futures.models import Signal, VirtualTrade
from app.futures.services.explanation_builder import ExplanationBuilder
from app.futures.services.ai_analyzer import AIAnalyzer
from app.futures.models.exchange_connector import ExchangeConnector
from app.futures.services.signal_orchestrator import SignalOrchestrator
from app.futures.models import VirtualTrade
router = APIRouter(tags=["futures"])

# Створюємо екземпляри сервісів
explanation_builder = ExplanationBuilder()
ai_analyzer = AIAnalyzer()
exchange_connector = ExchangeConnector()
signal_orchestrator = SignalOrchestrator()


@router.get("/health")
def health_check():
    """Проста перевірка роботи модуля ф'ючерсів"""
    return {
        "module": "futures_signals",
        "status": "active",
        "version": "0.0.1",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/test")
def test_endpoint():
    """Тестовий ендпоінт"""
    return {
        "message": "Futures module is working",
        "test_data": {
            "signal": "BTCUSDT LONG",
            "confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        }
    }


@router.post("/signals/generate")
def generate_signal(
    symbol: str = "BTC/USDT:USDT",
    timeframe: str = "1h",
    db: Session = Depends(get_db)
):
    """Згенерувати реальний AI-сигнал на основі ринкового аналізу"""
    
    # Використовуємо оркестратор для повного пайплайну
    analysis = signal_orchestrator.generate_signal(symbol, timeframe)
    
    if "error" in analysis:
        raise HTTPException(status_code=400, detail=analysis["error"])
    
    # Додаємо symbol до analysis для пояснення
    analysis['symbol'] = symbol
    analysis['timeframe'] = timeframe
    
    # Генеруємо пояснення на основі реального аналізу
    explanation = explanation_builder.build_explanation(analysis)
    
    # Зберігаємо в БД
    db_signal = Signal(
        symbol=symbol,
        direction=analysis["direction"],
        confidence=analysis["confidence"],
        reasoning_weights=analysis.get("factors", {}),
        explanation_text=explanation,
        entry_price=analysis["entry_price"],
        take_profit=analysis["take_profit"],
        stop_loss=analysis["stop_loss"],
        timeframe=timeframe,
        is_active=True,
        source="ai_analyzer_v2"
    )
    
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    
    return {
        "status": "success",
        "signal": {
            "id": db_signal.id,
            "symbol": symbol,
            "direction": analysis["direction"],
            "confidence": analysis["confidence"],
            "explanation": explanation,
            "factors": analysis.get("factors", {}),
            "entry_price": analysis["entry_price"],
            "take_profit": analysis["take_profit"],
            "stop_loss": analysis["stop_loss"],
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat()
        },
        "analysis_type": "market_based",
        "message": "Signal generated based on market analysis"
    }


@router.post("/signals/generate-multiple")
def generate_multiple_signals(
    symbols: List[str] = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"],
    timeframe: str = "1h",
    db: Session = Depends(get_db)
):
    """Згенерувати сигнали для кількох пар одночасно"""
    signals = signal_orchestrator.generate_multiple_signals(symbols)
    
    saved_signals = []
    for analysis in signals:
        if "error" not in analysis:
            analysis['symbol'] = analysis.get('symbol', '')
            analysis['timeframe'] = timeframe
            
            explanation = explanation_builder.build_explanation(analysis)
            
            db_signal = Signal(
                symbol=analysis["symbol"],
                direction=analysis["direction"],
                confidence=analysis["confidence"],
                reasoning_weights=analysis.get("factors", {}),
                explanation_text=explanation,
                entry_price=analysis["entry_price"],
                take_profit=analysis["take_profit"],
                stop_loss=analysis["stop_loss"],
                timeframe=timeframe,
                is_active=True,
                source="ai_analyzer_batch"
            )
            
            db.add(db_signal)
            saved_signals.append({
                "id": db_signal.id,
                "symbol": analysis["symbol"],
                "direction": analysis["direction"],
                "confidence": analysis["confidence"],
                "explanation": explanation
            })
    
    db.commit()
    
    return {
        "status": "success",
        "count": len(saved_signals),
        "signals": saved_signals,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/signals")
def get_signals(
    db: Session = Depends(get_db),
    limit: int = 10,
    active_only: bool = True
):
    """Отримати список сигналів з БД"""
    query = db.query(Signal)
    
    if active_only:
        query = query.filter(Signal.is_active == True)
    
    signals = query.order_by(Signal.created_at.desc()).limit(limit).all()
    
    return {
        "status": "success",
        "count": len(signals),
        "signals": [signal.to_dict() for signal in signals]
    }


@router.get("/signals/{signal_id}")
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db)
):
    """Отримати деталі конкретного сигналу"""
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return {
        "status": "success",
        "signal": signal.to_dict()
    }


@router.get("/explain")
def explain_signal(
    symbol: str = "BTC/USDT:USDT",
    direction: str = "long",
    confidence: float = 0.75,
    entry_price: Optional[float] = None,
    timeframe: str = "1h"
):
    """Отримати текстове пояснення для сигналу"""
    # Якщо не вказана ціна, отримуємо поточну з біржі
    if entry_price is None:
        try:
            ticker = exchange_connector.fetch_ticker(symbol)
            entry_price = ticker['last'] if ticker else 10000
        except:
            entry_price = 10000
    
    # Створюємо мок-об'єкт сигналу
    mock_signal = {
        'symbol': symbol,
        'direction': direction,
        'confidence': confidence,
        'entry_price': entry_price,
        'take_profit': entry_price * (1.03 if direction == "long" else 0.97),
        'stop_loss': entry_price * (0.98 if direction == "long" else 1.02),
        'timeframe': timeframe,
        'factors': {
            "trend_strength": confidence,
            "volume_confirmation": 0.7,
            "support_resistance": 0.6,
            "volatility": 0.5,
            "momentum": confidence * 0.9
        }
    }
    
    explanation = explanation_builder.build_explanation(mock_signal)
    
    return {
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "entry_price": entry_price,
        "explanation": explanation,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/market-data/{symbol}")
def get_market_data(
    symbol: str = "BTC/USDT:USDT",
    timeframe: str = "1h",
    limit: int = 100
):
    """Отримати ринкові дані для символу"""
    try:
        df = exchange_connector.fetch_ohlcv(symbol, timeframe, limit)
        
        return {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "data_count": len(df),
            "latest_price": float(df['close'].iloc[-1]) if len(df) > 0 else 0,
            "samples": df[['timestamp', 'close']].tail(5).to_dict('records') if len(df) > 0 else []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch market data: {str(e)}")


# ВІРТУАЛЬНІ УГОДИ API

@router.post("/virtual-trades", response_model=dict)
def create_virtual_trade(
    signal_id: int,
    entry_price: float,
    take_profit: float,
    stop_loss: float,
    db: Session = Depends(get_db)
):
    """
    Створити віртуальну угоду для тестування сигналу
    
    Args:
        signal_id: ID сигналу з БД
        entry_price: Ціна входу
        take_profit: Ціна take profit
        stop_loss: Ціна stop loss
    """
    # Перевіряємо чи існує сигнал
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    # Створюємо віртуальну угоду
    virtual_trade = VirtualTrade(
        signal_id=signal_id,
        entry_price=entry_price,
        take_profit=take_profit,
        stop_loss=stop_loss,
        current_price=entry_price,  # Початкова ціна = ціна входу
        status="active",
        pnl_percentage=0.0,
        pnl_amount=0.0
    )
    
    db.add(virtual_trade)
    db.commit()
    db.refresh(virtual_trade)
    
    return {
        "status": "success",
        "message": "Virtual trade created",
        "trade": virtual_trade.to_dict()
    }


@router.get("/virtual-trades", response_model=dict)
def get_virtual_trades(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Отримати список віртуальних угод"""
    query = db.query(VirtualTrade)
    
    if status:
        query = query.filter(VirtualTrade.status == status)
    
    trades = query.order_by(VirtualTrade.created_at.desc()).limit(limit).all()
    
    return {
        "status": "success",
        "count": len(trades),
        "trades": [trade.to_dict() for trade in trades]
    }


@router.get("/virtual-trades/{trade_id}", response_model=dict)
def get_virtual_trade(
    trade_id: int,
    db: Session = Depends(get_db)
):
    """Отримати деталі віртуальної угоди"""
    trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Virtual trade not found")
    
    return {
        "status": "success",
        "trade": trade.to_dict()
    }


@router.post("/virtual-trades/{trade_id}/update-price", response_model=dict)
def update_trade_price(
    trade_id: int,
    current_price: float,
    db: Session = Depends(get_db)
):
    """Оновити поточну ціну для віртуальної угоди"""
    trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Virtual trade not found")
    
    if trade.status != "active":
        raise HTTPException(status_code=400, detail=f"Trade is {trade.status}, cannot update")
    
    # Оновлюємо ціну та розраховуємо PnL
    old_status = trade.status
    trade.calculate_pnl(current_price)
    
    # Якщо статус змінився (досягнуто TP/SL), оновлюємо
    if trade.status != old_status and trade.status in ["tp_hit", "sl_hit"]:
        from sqlalchemy.sql import func
        trade.closed_at = func.now()
    
    db.commit()
    db.refresh(trade)
    
    return {
        "status": "success",
        "message": f"Price updated to {current_price}",
        "trade": trade.to_dict(),
        "pnl_update": {
            "old_status": old_status,
            "new_status": trade.status,
            "pnl_percentage": round(trade.pnl_percentage, 2),
            "pnl_amount": round(trade.pnl_amount, 2)
        }
    }


@router.delete("/virtual-trades/{trade_id}", response_model=dict)
def delete_virtual_trade(
    trade_id: int,
    db: Session = Depends(get_db)
):
    """Видалити віртуальну угоду"""
    trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Virtual trade not found")
    
    db.delete(trade)
    db.commit()
    
    return {
        "status": "success",
        "message": "Virtual trade deleted"
    }


@router.get("/signals/{signal_id}/virtual-trades")
def get_signal_virtual_trades(
    signal_id: int,
    db: Session = Depends(get_db)
):
    """Отримати всі віртуальні угоди для конкретного сигналу"""
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    trades = db.query(VirtualTrade).filter(
        VirtualTrade.signal_id == signal_id
    ).order_by(VirtualTrade.created_at.desc()).all()
    
    return {
        "status": "success",
        "signal": signal.to_dict(),
        "count": len(trades),
        "trades": [trade.to_dict() for trade in trades]
    }