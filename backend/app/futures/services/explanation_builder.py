# backend/app/futures/services/explanation_builder.py
from typing import Dict

class ExplanationBuilder:
    def __init__(self):
        self.templates = {
            'long': {
                'strong': "🟢 СИЛЬНИЙ ПОЗИТИВНИЙ СИГНАЛ. Тренд чіткий вгору з впевненістю {confidence}%. "
                         "RSI ({rsi}) показує недооціненість, MACD підтверджує зростання. "
                         "Входимо довгими з TP: ${tp} та SL: ${sl}.",
                'medium': "🟡 ПОМІРНИЙ ПОЗИТИВНИЙ СИГНАЛ. Потенціал для росту є з впевненістю {confidence}%. "
                         "Рекомендовано обережне входження. TP: ${tp}, SL: ${sl}.",
                'weak': "⚪ СЛАБКИЙ СИГНАЛ. Незначні позитивні ознаки ({confidence}%). "
                       "Чекаємо підтвердження. TP: ${tp}, SL: ${sl}."
            },
            'short': {
                'strong': "🔴 СИЛЬНИЙ НЕГАТИВНИЙ СИГНАЛ. Тренд чіткий вниз з впевненістю {confidence}%. "
                         "RSI ({rsi}) показує перекупленість. Входимо короткими з TP: ${tp} та SL: ${sl}.",
                'medium': "🟠 ПОМІРНИЙ НЕГАТИВНИЙ СИГНАЛ. Потенціал для падіння є з впевненістю {confidence}%. "
                         "Обережне входження. TP: ${tp}, SL: ${sl}.",
                'weak': "⚪ СЛАБКИЙ СИГНАЛ. Незначні негативні ознаки ({confidence}%). "
                       "Чекаємо підтвердження. TP: ${tp}, SL: ${sl}."
            }
        }
    
    def build_explanation(self, signal_data: Dict) -> str:
        """Генерація текстового пояснення на основі сигналу"""
        direction = signal_data.get('direction', 'neutral')
        confidence = signal_data.get('confidence', 0)
        rsi = signal_data.get('indicators', {}).get('rsi', 50)
        
        # Визначаємо силу сигналу
        if confidence > 0.75:
            strength = 'strong'
        elif confidence > 0.6:
            strength = 'medium'
        else:
            strength = 'weak'
        
        # Беремо шаблон
        template = self.templates.get(direction, {}).get(strength, "Немає чіткого сигналу.")
        
        # Форматуємо
        explanation = template.format(
            confidence=int(confidence * 100),
            rsi=round(rsi, 1),
            tp=round(signal_data.get('take_profit', 0), 2),
            sl=round(signal_data.get('stop_loss', 0), 2),
            entry=round(signal_data.get('entry_price', 0), 2)
        )
        
        return explanation