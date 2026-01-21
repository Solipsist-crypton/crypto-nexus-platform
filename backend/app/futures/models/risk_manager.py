# backend/modules/risk_manager.py
class RiskManager:
    def __init__(self, max_position_size: float = 0.1, max_daily_loss: float = 0.05):
        self.max_position_size = max_position_size  # Макс 10% портфеля на позицію
        self.max_daily_loss = max_daily_loss  # Макс 5% денного збитку
        self.positions = []
        self.daily_pnl = 0
        
    def calculate_position_size(self, portfolio_value: float, confidence: float, 
                               stop_loss_distance: float) -> float:
        """Розрахунок розміру позиції згідно з Kelly Criterion"""
        # Параметри ризику
        win_rate = 0.55  # Припущення про win rate
        risk_reward = 2.0  # Припущення про співвідношення ризик/прибуток
        
        # Kelly Criterion
        kelly = ((win_rate * risk_reward) - (1 - win_rate)) / risk_reward
        
        # Консервативна версія (половина Kelly)
        position_kelly = (kelly * confidence) / 2
        
        # Обмеження максимального розміру
        max_size = self.max_position_size * portfolio_value
        position_size = min(position_kelly * portfolio_value, max_size)
        
        # Перевірка на основі stop loss
        risk_amount = portfolio_value * self.max_daily_loss
        sl_based_size = risk_amount / stop_loss_distance
        
        return min(position_size, sl_based_size)
    
    def check_market_conditions(self, volatility: float, funding_rate: float) -> bool:
        """Перевірка ринкових умов для входу в позицію"""
        # Високий фандинг рейт може свідчити про перекупленість
        if abs(funding_rate) > 0.0005:  # 0.05%
            return False
        
        # Занадто висока волатильність
        if volatility > 0.10:  # 10%
            return False
            
        return True