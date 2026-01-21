"""
ExplanationBuilder для генерації текстових пояснень сигналів.
"""

import random
from typing import Dict, List

class ExplanationBuilder:
    """Генерує людсько-зрозумілі пояснення на основі AI-аналізу"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        return {
            "trend": [
                "{symbol} демонструє {strength} {direction_ua} тренд ({confidence}%).",
                "Технічний аналіз виявляє {direction_ua} динаміку для {symbol}.",
                "Індикатори підтверджують {direction_ua} позицію для {symbol}."
            ],
            "level": [
                "{symbol} тестує рівень {level_type}, що формує {direction_ua} сигнал.",
                "Ціна наближається до {level_type} рівня, створюючи {direction_ua} можливість.",
                "Прорив {level_type} рівня підтверджує {direction_ua} сигнал."
            ]
        }
    
    def build_explanation(self, symbol: str, direction: str, confidence: float, **kwargs) -> str:
        """Основна функція генерації пояснення"""
        
        # Переклад напрямку
        direction_ua = "позитивний" if direction == "long" else "негативний"
        
        # Визначення сили сигналу
        if confidence > 0.8:
            strength = "дуже сильний"
        elif confidence > 0.65:
            strength = "сильний"
        else:
            strength = "помірний"
        
        # Вибір типу шаблону
        template_type = "trend"
        level_type = "підтримки" if direction == "long" else "опору"
        
        # Вибір випадкового шаблону
        template = random.choice(self.templates[template_type])
        
        # Форматування
        explanation = template.format(
            symbol=symbol,
            direction_ua=direction_ua,
            strength=strength,
            confidence=int(confidence * 100),
            level_type=level_type
        )
        
        # Додавання рекомендації
        if confidence > 0.7:
            explanation += " Рекомендовано розглянути позицію."
        elif confidence > 0.5:
            explanation += " Можлива позиція з обережністю."
        
        return explanation


# Глобальний екземпляр
explanation_builder = ExplanationBuilder()