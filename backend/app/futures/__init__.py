# Futures module exports
from .models import Signal, VirtualTrade
from .services.explanation_builder import ExplanationBuilder, explanation_builder

__all__ = [
    "Signal", 
    "VirtualTrade", 
    "ExplanationBuilder", 
    "explanation_builder"
]