import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
from typing import Dict, List, Any

class InstitutionalPortfolioOptimizer:
    def __init__(self, target_volatility: float = 0.12):
        self.target_volatility = target_volatility

    def compute_ledoit_wolf_cov(self, returns_df: pd.DataFrame) -> np.ndarray:
        lw = LedoitWolf()
        shrunk_cov = lw.fit(returns_df.values).covariance_
        return shrunk_cov

    def _risk_budget_objective(self, weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        if portfolio_vol <= 0:
            return 0.0
            
        marginal_risk_contrib = np.dot(cov_matrix, weights) / portfolio_vol
        risk_contrib = weights * marginal_risk_contrib
        
        num_assets = len(weights)
        target_risk = portfolio_vol / num_assets
        return float(np.sum((risk_contrib - target_risk) ** 2))

    def solve_erc_weights(self, returns_df: pd.DataFrame, signals: Dict[str, float]) -> Dict[str, float]:
        symbols = list(returns_df.columns)
        num_assets = len(symbols)
        if num_assets == 0:
            return {}

        cov_matrix = self.compute_ledoit_wolf_cov(returns_df)
        init_weights = np.ones(num_assets) / num_assets
        bounds = [(0.02, 0.40) for _ in range(num_assets)]
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        res = minimize(
            self._risk_budget_objective,
            init_weights,
            args=(cov_matrix,),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        base_weights = res.x if res.success else init_weights
        final_weights = {}
        for idx, symbol in enumerate(symbols):
            sig = signals.get(symbol, 0.0)
            adjusted_w = base_weights[idx] * (1.0 + (0.3 * sig))
            final_weights[symbol] = max(0.0, float(adjusted_w))
            
        total_w = sum(final_weights.values())
        if total_w <= 0:
            return {s: 1.0 / num_assets for s in symbols}
        return {s: w / total_w for s, w in final_weights.items()}
