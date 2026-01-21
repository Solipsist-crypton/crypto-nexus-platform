"""
ExplanationBuilder для генерації текстових пояснень сигналів.
Фаза 1 з roadmap.
"""

import random
from typing import Dict, List
from datetime import datetime

class ExplanationBuilder:
    """Генерує людсько-зрозумілі пояснення на основі AI-аналізу"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Завантажує шаблони пояснень"""
        return {
            "trend_based": [
                "{symbol} демонструє {trend_strength} {direction_ua} тренд з підтвердженням обсягів ({confidence_pct}).",
                "Технічний аналіз виявляє {trend_strength} {direction_ua} динаміку для {symbol}.",
                "Індикатори тренду підтверджують {direction_ua} позицію для {symbol} з впевненістю {confidence_pct}."
            ],
            "level_based": [
                "{symbol} тестує ключовий рівень {level_type}, що формує {direction_ua} сигнал.",
                "Ціна наближається до {level_type} рівня, створюючи можливість для {direction_ua} позиції.",
                "Прорив {level_type} рівня підтверджує {direction_ua} сигнал для {symbol}."
            ],
            "volatility_based": [
                "Зростання волатильності {symbol} посилює {direction_ua} сигнал ({confidence_pct}).",
                "Стиснення волатильності передбачає значний рух {direction_ua} для {symbol}.",
                "Волатильність повертається до середніх значень, підтримуючи {direction_ua} позицію."
            ]
        }
    
    def build_explanation(
        self,
        symbol: str,
        direction: str,
        confidence: float,
        factors: Dict[str, float] = None,
        timeframe: str = "1h"
    ) -> str:
        """
        Генерує пояснення на основі факторів AI.
        """
        # Перекладаємо direction
        direction_ua = "позитивний" if direction == "long" else "негативний"
        confidence_pct = f"{confidence:.0%}"
        
        # Якщо фактори не надано, створюємо базові
        if factors is None:
            factors = {
                "trend_strength": round(random.uniform(0.5, 0.9), 2),
                "volume_confirmation": round(random.uniform(0.4, 0.8), 2),
                "support_resistance": round(random.uniform(0.6, 0.95), 2),
                "volatility": round(random.uniform(0.3, 0.7), 2),
                "momentum": round(random.uniform(0.5, 0.85), 2)
            }
        
        # Визначаємо силу сигналу
        if confidence > 0.8:
            strength = "дуже сильний"
        elif confidence > 0.65:
            strength = "сильний"
        elif confidence > 0.5:
            strength = "помірний"
        else:
            strength = "слабкий"
        
        # Вибираємо тип шаблону
        if factors.get("trend_strength", 0) > factors.get("support_resistance", 0):
            template_type = "trend_based"
            level_type = "підтримки" if direction == "long" else "опору"
        else:
            template_type = "level_based"
            level_type = "підтримки" if direction == "long" else "опору"
        
        # Вибираємо випадковий шаблон
        template = random.choice(self.templates[template_type])
        
        try:
            # Формуємо пояснення
            explanation = template.format(
                symbol=symbol,
                direction_ua=direction_ua,
                trend_strength=strength,
                confidence_pct=confidence_pct,
                level_type=level_type
            )
            
            # Додаємо топ-фактори
            top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:2]
            if top_factors:
                factor_names = {
                    "trend_strength": "сила тренду",
                    "volume_confirmation": "обсяги",
                    "support_resistance": "рівні підтримки/опору",
                    "volatility": "волатильність",
                    "momentum": "імпульс"
                }
                factor_text = []
                for factor_name, factor_value in top_factors:
                    if factor_value > 0.6:
                        name = factor_names.get(factor_name, factor_name)
                        factor_text.append(f"{name} ({factor_value:.0%})")
                
                if factor_text:
                    explanation += f" Ключові фактори: {', '.join(factor_text)}."
            
            # Додаємо рекомендацію
            if confidence > 0.7:
                explanation += " Рекомендовано розглянути позицію."
            elif confidence > 0.5:
                explanation += " Можлива позиція з обережністю."
            
            return explanation
            
        except KeyError as e:
            # Якщо відсутня змінна в шаблоні
            return f"{symbol} демонструє {direction_ua} сигнал з впевненістю {confidence_pct}."
    
    def build_detailed_report(self, **kwargs):
        """Заглушка для сумісності"""
        return {"explanation": self.build_explanation(**kwargs)}


# Глобальний екземпляр для імпорту
explanation_builder = ExplanationBuilder()