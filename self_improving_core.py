import numpy as np
from scipy.stats import skew, kurtosis, norm
from typing import List, Dict, Any

class SelfImprovingAdaptiveCore:
    def __init__(self):
        self.params = {
            "vpin_threshold": 0.65,
            "kelly_fraction": 0.50,
            "max_drawdown_limit": 0.05
        }

    def compute_deflated_sharpe_ratio(self, returns: np.ndarray, num_trials: int = 10) -> float:
        N = len(returns)
        if N < 10:
            return 0.0
            
        sr_hat = np.mean(returns) / (np.std(returns) + 1e-6)
        skew_hat = skew(returns)
        kurt_hat = kurtosis(returns, fisher=False)
        
        euler_mascheroni = 0.5772156649
        max_expected_sr = (1 - euler_mascheroni) * norm.ppf(1 - 1/num_trials) + euler_mascheroni * norm.ppf(1 - 1/(num_trials * np.e))
        
        sr_std = np.sqrt((1 - skew_hat * sr_hat + ((kurt_hat - 1) / 4) * (sr_hat ** 2)) / (N - 1))
        dsr_z_stat = (sr_hat - max_expected_sr) / sr_std
        return float(norm.cdf(dsr_z_stat))

    def self_tune_hyperparameters(self, trade_returns: List[float]):
        if len(trade_returns) < 15:
            return

        returns_arr = np.array(trade_returns)
        dsr = self.compute_deflated_sharpe_ratio(returns_arr)
        
        if dsr < 0.80:
            self.params["kelly_fraction"] = max(0.15, self.params["kelly_fraction"] - 0.05)
            self.params["vpin_threshold"] = max(0.50, self.params["vpin_threshold"] - 0.02)
        elif dsr > 0.95:
            self.params["kelly_fraction"] = min(0.65, self.params["kelly_fraction"] + 0.02)
