import numpy as np
import pandas as pd

class PortfolioOptimizer:
    """
    محرك تحسين أوزان المحفظة باستخدام Risk Parity و Black-Litterman
    """
    def __init__(self, returns_df: pd.DataFrame):
        self.returns = returns_df
        self.cov_matrix = returns_df.cov() * 252

    def risk_parity_weights(self) -> np.ndarray:
        variances = np.diag(self.cov_matrix)
        inv_vol = 1.0 / np.sqrt(np.maximum(variances, 1e-9))
        weights = inv_vol / np.sum(inv_vol)
        return weights

    def black_litterman_allocation(self, market_caps: np.ndarray, investor_views: np.ndarray) -> np.ndarray:
        num_assets = len(market_caps)
        total_cap = np.sum(market_caps)
        w_market = market_caps / (total_cap + 1e-9)
        
        tau = 0.05
        pi = 2.5 * np.dot(self.cov_matrix, w_market)
        
        omega = np.diag(np.diag(tau * self.cov_matrix))
        P = np.eye(num_assets)
        
        try:
            inv_tau_cov = np.linalg.inv(tau * self.cov_matrix + np.eye(num_assets)*1e-6)
            inv_omega = np.linalg.inv(omega + np.eye(num_assets)*1e-6)
            
            post_cov = np.linalg.inv(inv_tau_cov + np.dot(np.dot(P.T, inv_omega), P))
            post_returns = np.dot(post_cov, np.dot(inv_tau_cov, pi) + np.dot(np.dot(P.T, inv_omega), investor_views))
            
            opt_weights = np.dot(np.linalg.inv(self.cov_matrix + np.eye(num_assets)*1e-6), post_returns)
            opt_weights /= (np.sum(np.abs(opt_weights)) + 1e-9)
            return opt_weights
        except Exception:
            return self.risk_parity_weights()
