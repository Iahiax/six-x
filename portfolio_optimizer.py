import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
from typing import Dict, List, Any

class InstitutionalPortfolioOptimizer:
    """
    محرك استمثال المحفظة: Ledoit-Wolf Shrinkage و Equal Risk Contribution (ERC)
    """
    def __init__(self, target_volatility: float = 0.12):
        self.target_volatility = target_volatility

    def compute_ledoit_wolf_cov(self, returns_df: pd.DataFrame) -> np.ndarray:
        """
        حساب مصفوفة التباين المقلّمة المستقرة:
        $$\Sigma_{shrunk} = \delta F + (1 - \delta) S$$
        """
        lw = LedoitWolf()
        shrunk_cov = lw.fit(returns_df.values).covariance_
        return shrunk_cov

    def _risk_budget_objective(self, weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        """
        دالة الهدف لتحديد أوزان مساهمة المخاطر المتساوية (ERC Risk Parity)
        """
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        if portfolio_vol <= 0:
            return 0.0
            
        marginal_risk_contrib = np.dot(cov_matrix, weights) / portfolio_vol
        risk_contrib = weights * marginal_risk_contrib
        
        # تقليل الفروقات بين مساهمات المخاطر لكل أصل
        num_assets = len(weights)
        target_risk = portfolio_vol / num_assets
        return float(np.sum((risk_contrib - target_risk) ** 2))

    def solve_erc_weights(self, returns_df: pd.DataFrame, signals: Dict[str, float]) -> Dict[str, float]:
        """
        حل أوزان ERC وتعديلها بحسب إشارات الذكاء الاصطناعي
        """
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
        
        # تعديل الأوزان الأساسية بإشارات الذكاء الاصطناعي
        final_weights = {}
        for idx, symbol in enumerate(symbols):
            sig = signals.get(symbol, 0.0)
            # تعديل الوزن بحد أقصى ±30% بناءً على إشارة النموذج
            adjusted_w = base_weights[idx] * (1.0 + (0.3 * sig))
            final_weights[symbol] = float(adjusted_w)
            
        # إعادة المعايرة ليكون مجموع الأوزان = 1.0
        total_w = sum(final_weights.values())
        return {s: w / total_w for s, w in final_weights.items()}
