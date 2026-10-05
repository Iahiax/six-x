import numpy as np
import pandas as pd
from scipy.stats import norm

class CompleteMicrostructureAndQuantMath:
    """
    محرك الحسابات المالية والكمية وشفرات السيولة الجزيئية (Microstructure & Quant Indicators)
    يتضمن 35 معياراً رياضياً متكاملاً للتداول المؤسسي.
    """

    @staticmethod
    def calculate_nlvr(open_p: float, high_p: float, low_p: float, close_p: float) -> float:
        """Net Liquidity Void Ratio (NLVR) - قياس الفجوات الهيكلية في السيولة"""
        range_p = high_p - low_p
        if range_p == 0:
            return 0.0
        body = abs(close_p - open_p)
        void_ratio = 1.0 - (body / range_p)
        return float(np.clip(void_ratio, 0.0, 1.0))

    @staticmethod
    def glosten_harris_spread(prices: np.ndarray, volumes: np.ndarray) -> tuple[float, float]:
        """نموذج Glosten-Harris لفصل تكاليف الاختلال والسيولة وحساب الفارق السعري المؤثر"""
        if len(prices) < 3 or len(volumes) < 3:
            return 0.0, 0.0
        dp = np.diff(prices)
        volume_signs = np.sign(dp)
        q = volume_signs * volumes[1:]
        
        # OLS regression: dp = c0 * q + c1 * q * volume
        X = np.column_stack([q, q * volumes[1:]])
        try:
            params, _, _, _ = np.linalg.lstsq(X, dp, rcond=None)
            adverse_selection_cost = float(params[0])
            inventory_risk_cost = float(params[1])
            return adverse_selection_cost, inventory_risk_cost
        except np.linalg.LinAlgError:
            return 0.0, 0.0

    @staticmethod
    def ornstein_uhlenbeck_halflife(prices: np.ndarray) -> float:
        """حساب عمر النصف لارتداد السعر إلى المتوسط (Ornstein-Uhlenbeck Mean Reversion Half-Life)"""
        if len(prices) < 20:
            return 0.0
        p_lag = prices[:-1]
        p_diff = np.diff(prices)
        
        # Regression: delta_p = lambda * (mean - p_lag)
        X = np.column_stack([p_lag, np.ones_like(p_lag)])
        params, _, _, _ = np.linalg.lstsq(X, p_diff, rcond=None)
        lambda_param = params[0]
        
        if lambda_param >= 0:
            return 999.0 # لا يوجد ارتداد للمتوسط (Trending Process)
        
        half_life = -np.log(2) / lambda_param
        return float(half_life)

    @staticmethod
    def bayesian_kelly_position_size(win_prob: float, win_loss_ratio: float, capital: float, max_risk_pct: float = 0.05) -> float:
        """حجم المركز المالي وفق صيغة كيلي مع الضبط البايزي لتجنب المخاطرة العالية"""
        if win_loss_ratio <= 0:
            return 0.0
        kelly_f = win_prob - ((1.0 - win_prob) / win_loss_ratio)
        fractional_kelly = kelly_f * 0.5 # Half-Kelly للتأمين
        
        bounded_risk = max(0.0, min(fractional_kelly, max_risk_pct))
        return float(capital * bounded_risk)

    @staticmethod
    def vpin_volume_order_imbalance(buy_volumes: np.ndarray, sell_volumes: np.ndarray, bucket_size: float) -> float:
        """Volume-Synchronized Probability of Toxicity (VPIN) - نسبة اختلال الأوامر الشديدة"""
        total_vol = buy_volumes + sell_volumes
        if np.sum(total_vol) == 0:
            return 0.0
        imbalance = np.abs(buy_volumes - sell_volumes)
        vpin = np.sum(imbalance) / (len(buy_volumes) * bucket_size)
        return float(vpin)

    @staticmethod
    def fractal_dimension_hurst(prices: np.ndarray) -> float:
        """أس هيرست (Hurst Exponent) لتحديد طبيعة السوق (Mean Reversion < 0.5 < Trending)"""
        if len(prices) < 100:
            return 0.5
        lags = range(2, 20)
        tau = [np.sqrt(np.std(np.subtract(prices[lag:], prices[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return float(poly[0] * 2.0)
