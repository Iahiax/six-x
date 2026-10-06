import numpy as np
from scipy.stats import skew, kurtosis, norm
from typing import List, Dict, Any

class SelfImprovingAdaptiveCore:
    """
    العقل التكيّفي الفائق: حساب DSR والتعلم الذاتي التلقائي
    """
    def __init__(self):
        self.params = {
            "vpin_threshold": 0.65,
            "kelly_fraction": 0.50,
            "max_drawdown_limit": 0.05
        }

    def compute_deflated_sharpe_ratio(self, returns: np.ndarray, num_trials: int = 10) -> float:
        """
        حساب نسبة شارب التصحيحية (DSR) لمنع الإفراط في التفاؤل الإحصائي
        """
        N = len(returns)
        if N < 10:
            return 0.0
            
        sr_hat = np.mean(returns) / (np.std(returns) + 1e-6)
        skew_hat = skew(returns)
        kurt_hat = kurtosis(returns, fisher=False) # Pearson definition
        
        # تقدير الحد الأقصى المتوقع لشارب بالحظ
        euler_mascheroni = 0.5772156649
        max_expected_sr = (1 - euler_mascheroni) * norm.ppf(1 - 1/num_trials) + euler_mascheroni * norm.ppf(1 - 1/(num_trials * np.e))
        
        # الانحراف المعياري لنسبة شارب المحسوبة
        sr_std = np.sqrt((1 - skew_hat * sr_hat + ((kurt_hat - 1) / 4) * (sr_hat ** 2)) / (N - 1))
        
        dsr_z_stat = (sr_hat - max_expected_sr) / sr_std
        dsr_prob = norm.cdf(dsr_z_stat)
        
        return float(dsr_prob)

    def self_tune_hyperparameters(self, trade_returns: List[float]):
        """
        ضبط المعاملات أوتوماتيكياً بناءً على قيمة DSR والأداء الفعلي
        """
        if len(trade_returns) < 15:
            return

        returns_arr = np.array(trade_returns)
        dsr = self.compute_deflated_sharpe_ratio(returns_arr)
        
        if dsr < 0.80:
            # تخفيض المخاطرة ورفع الصرامة عند تراجع DSR
            self.params["kelly_fraction"] = max(0.15, self.params["kelly_fraction"] - 0.05)
            self.params["vpin_threshold"] = max(0.50, self.params["vpin_threshold"] - 0.02)
        elif dsr > 0.95:
            # رفع حد التوسع بحذر عند ارتفاع DSR
            self.params["kelly_fraction"] = min(0.65, self.params["kelly_fraction"] + 0.02)
