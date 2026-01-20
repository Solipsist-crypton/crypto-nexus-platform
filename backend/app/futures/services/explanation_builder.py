class ExplanationBuilder:
    @staticmethod
    def build_explanation(symbol, direction, confidence, factors=None):
        return f"AI сигнал для {symbol} на {direction} з впевненістю {confidence:.0%}"

explanation_builder = ExplanationBuilder()