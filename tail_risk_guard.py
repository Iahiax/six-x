import numpy as np
import pandas as pd
import logging
from config import config

logger = logging.getLogger("TailRiskGuard")

class TailRiskGuard:
    """
    محرك إدارة مخاطر الذيل وحساب VaR / CVaR
    """
    @staticmethod
    def calculate_historical_var(returns: pd.Series, confidence_level: float = 0.99) -> float:
        if returns.empty:
            return 0.0
        return float(np.percentile(returns, (1.0 - confidence_level) * 100))

    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.99) -> float:
        var = TailRiskGuard.calculate_historical_var(returns, confidence_level)
        tail_losses = returns[returns <= var]
        if tail_losses.empty:
            return var
        return float(tail_losses.mean())

    def evaluate_risk_clearance(self, portfolio_returns: pd.Series, current_drawdown: float) -> float:
        if current_drawdown > config.MAX_DRAWDOWN_LIMIT:
            logger.warning(f"تجاوز التراجع الحد المسموح: {current_drawdown * 100:.2f}%")
            return 0.1

        cvar_99 = self.calculate_cvar(portfolio_returns, config.VAR_CONFIDENCE_LEVEL)
        risk_score = 1.0 - abs(cvar_99) * 10
        return float(np.clip(risk_score, 0.0, 1.0))
