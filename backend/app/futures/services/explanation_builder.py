# backend/app/futures/services/explanation_builder.py
from typing import Dict

class ExplanationBuilder:
    def __init__(self):
        self.templates = {
            'long': {
                'strong': "🟢 **СИЛЬНИЙ ЛОНГ СИГНАЛ** для {symbol}\n"
                         "• Впевненість: {confidence}%\n"
                         "• Вхід: ${entry}\n"
                         "• Take Profit: ${tp}\n"
                         "• Stop Loss: ${sl}\n"
                         "• Часфрейм: {timeframe}\n"
                         "• Фактори: {factors_count} позитивних",
                'medium': "🟡 **ПОМІРНИЙ ЛОНГ СИГНАЛ** для {symbol}\n"
                         "• Впевненість: {confidence}%\n"
                         "• Вхід: ${entry}\n"
                         "• Take Profit: ${tp}\n"
                         "• Stop Loss: ${sl}",
                'weak': "⚪ **СЛАБКИЙ СИГНАЛ** для {symbol}\n"
                       "• Впевненість: {confidence}%\n"
                       "• Чекаємо підтвердження перед входом"
            },
            'short': {
                'strong': "🔴 **СИЛЬНИЙ ШОРТ СИГНАЛ** для {symbol}\n"
                         "• Впевненість: {confidence}%\n"
                         "• Вхід: ${entry}\n"
                         "• Take Profit: ${tp}\n"
                         "• Stop Loss: ${sl}\n"
                         "• Часфрейм: {timeframe}",
                'medium': "🟠 **ПОМІРНИЙ ШОРТ СИГНАЛ** для {symbol}\n"
                         "• Впевненість: {confidence}%\n"
                         "• Вхід: ${entry}\n"
                         "• Take Profit: ${tp}\n"
                         "• Stop Loss: ${sl}",
                'weak': "⚪ **СЛАБКИЙ СИГНАЛ** для {symbol}\n"
                       "• Впевненість: {confidence}%\n"
                       "• Обережно, ризиковано"
            }
        }
    
    def build_explanation(self, signal_data: Dict) -> str:
        """Генерація текстового пояснення"""
        direction = signal_data.get('direction', 'neutral')
        confidence = signal_data.get('confidence', 0) * 100
        
        # Визначаємо силу сигналу
        if confidence > 75:
            strength = 'strong'
        elif confidence > 60:
            strength = 'medium'
        else:
            strength = 'weak'
        
        # Беремо шаблон
        template = self.templates.get(direction, {}).get(
            strength, 
            f"📊 Сигнал для {signal_data.get('symbol', 'Unknown')}: {direction} ({confidence}%)"
        )
        
        # Форматуємо
        factors = signal_data.get('factors', {})
        # factors_count = len([v for v in factors.values() if v > 0.6]) if isinstance(factors, dict) else 0
        factors_count = 0
        if isinstance(factors, dict):
            for v in factors.values():
                try:
                    if float(v) > 0.6:  # Спробувати конвертувати в число
                        factors_count += 1
                except (ValueError, TypeError):
                     continue

        explanation = template.format(
            symbol=signal_data.get('symbol', 'Unknown'),
            confidence=int(confidence),
            entry=round(signal_data.get('entry_price', 0), 2),
            tp=round(signal_data.get('take_profit', 0), 2),
            sl=round(signal_data.get('stop_loss', 0), 2),
            timeframe=signal_data.get('timeframe', '1h'),
            factors_count=factors_count
        )
        
        return explanation