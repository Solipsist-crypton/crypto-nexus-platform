"""
ExplanationBuilder для генерації текстових пояснень сигналів.
Фаза 1 з roadmap: "Створення ExplanationBuilder для генерування текстового обґрунтування"
"""

import json
from typing import Dict, Any, List
from datetime import datetime
import random

class ExplanationBuilder:
    """Генерує людсько-зрозумілі пояснення на основі AI-аналізу"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.factors_descriptions = {
            "trend_strength": "сила тренду",
            "volume_confirmation": "підтвердження обсягами",
            "support_resistance": "рівні підтримки/опору",
            "volatility": "рівень волатильності",
            "momentum": "імпульс ринку",
            "market_sentiment": "ринкові настрої",
            "technical_indicators": "технічні індикатори"
        }
    
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
        
        Args:
            symbol: Торгова пара (BTCUSDT)
            direction: Напрямок (long/short)
            confidence: Рівень впевненості AI (0-1)
            factors: Словник з вагами факторів
            timeframe: Таймфрейм аналізу
            
        Returns:
            Текстове пояснення
        """
        # Перекладаємо direction
        direction_ua = "позитивний" if direction == "long" else "негативний"
        direction_action = "купувати" if direction == "long" else "продавати"
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
        
        # Визначаємо основний фактор
        main_factor = max(factors, key=factors.get)
        main_factor_value = factors[main_factor]
        
        # Визначаємо силу сигналу
        if confidence > 0.8:
            strength = "дуже сильний"
        elif confidence > 0.65:
            strength = "сильний"
        elif confidence > 0.5:
            strength = "помірний"
        else:
            strength = "слабкий"
        
        # Вибираємо тип шаблону на основі основного фактора
        if main_factor in ["trend_strength", "momentum"]:
            template_type = "trend_based"
            level_type = "підтримки" if direction == "long" else "опору"
        elif main_factor == "support_resistance":
            template_type = "level_based"
            level_type = "підтримки" if direction == "long" else "опору"
        else:
            template_type = "volatility_based"
            level_type = ""
        
        # Вибираємо випадковий шаблон
        template = random.choice(self.templates[template_type])
        
        # Формуємо пояснення
        explanation = template.format(
            symbol=symbol,
            direction_ua=direction_ua,
            trend_strength=strength,
            confidence_pct=confidence_pct,
            level_type=level_type
        )
        
        # Додаємо деталі про основні фактори
        top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:3]
        factor_details = []
        
        for factor_name, factor_value in top_factors:
            if factor_value > 0.6:  # Тільки значні фактори
                desc = self.factors_descriptions.get(factor_name, factor_name)
                factor_details.append(f"{desc} ({factor_value:.0%})")
        
        if factor_details:
            explanation += f" Ключові фактори: {', '.join(factor_details)}."
        
        # Додаємо рекомендацію
        if confidence > 0.7:
            explanation += f" Рекомендовано розглянути {direction_action} позицію."
        elif confidence > 0.5:
            explanation += f" Можливо {direction_action} позиціювання з обережністю."
        else:
            explanation += " Потребує додаткового підтвердження."
        
        return explanation
    
    def build_detailed_report(
        self,
        symbol: str,
        direction: str,
        confidence: float,
        factors: Dict[str, float],
        entry_price: float = None,
        take_profit: float = None,
        stop_loss: float = None
    ) -> Dict[str, Any]:
        """Генерує детальний звіт з поясненням"""
        
        explanation = self.build_explanation(
            symbol=symbol,
            direction=direction,
            confidence=confidence,
            factors=factors
        )
        
        report = {
            "symbol": symbol,
            "direction": direction,
            "confidence": confidence,
            "explanation": explanation,
            "factors": factors,
            "generated_at": datetime.now().isoformat(),
            "version": "ai_v1"
        }
        
        # Додаємо цінові рівні якщо є
        if entry_price:
            report["entry_price"] = entry_price
            report["take_profit"] = take_profit
            report["stop_loss"] = stop_loss
            
            if take_profit and stop_loss:
                # Розрахунок ризик-прибуток
                risk_reward = abs((take_profit - entry_price) / (entry_price - stop_loss))
                report["risk_reward_ratio"] = round(risk_reward, 2)
                report["potential_profit_pct"] = round(abs((take_profit - entry_price) / entry_price * 100), 2)
                report["potential_loss_pct"] = round(abs((stop_loss - entry_price) / entry_price * 100), 2)
        
        return report


# Глобальний екземпляр для імпорту
explanation_builder = ExplanationBuilder()