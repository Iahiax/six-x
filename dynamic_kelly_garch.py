import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("KellyGarchRisk")

class DynamicKellyGarchRiskEngine:
    """
    حساب الحجم الأمثل للصفقة عبر معيار كيلي الجزئي المدمج مع توقعات تقلبات GARCH(1,1)
    """
    def __init__(self, omega: float = 0.00001, alpha: float = 0.1, beta: float = 0.85):
        self.omega = omega
        self.alpha = alpha
        self.beta = beta

    def predict_garch_volatility(self, returns: np.ndarray) -> float:
        """
        التنبؤ بتقلبات الفترة القادمة باستخدام نموذج GARCH(1,1)
        """
        if len(returns) < 10:
            return float(np.std(returns)) if len(returns) > 1 else 0.01

        variance = float(np.var(returns))
        for r in returns[-30:]:
            variance = self.omega + (self.alpha * (r ** 2)) + (self.beta * variance)
        
        return float(np.sqrt(variance))

    def calculate_fractional_kelly_position(self, win_rate: float, win_loss_ratio: float, 
                                            capital: float, current_returns: np.ndarray, 
                                            fraction: float = 0.25) -> float:
        """
        حساب المبالغ المخصصة مع مراعاة مخاطر الذيل
        """
        if win_loss_ratio <= 0:
            return 0.0

        # معيار كيلي الكامل (Full Kelly)
        full_kelly = win_rate - ((1.0 - win_rate) / win_loss_ratio)
        if full_kelly <= 0:
            return 0.0

        # تعديل كيلي بناءً على تقلبات GARCH
        predicted_vol = self.predict_garch_volatility(current_returns)
        vol_penalty = 1.0 / (1.0 + (predicted_vol * 100))

        # كيلي الجزئي المعدل بالتقلبات (Fractional Volatility-Adjusted Kelly)
        adjusted_fraction = fraction * vol_penalty
        allocated_capital = capital * full_kelly * adjusted_fraction

        logger.info(f"حجم التخصيص المحسوب: {allocated_capital:.2f}$ (معيار كيلي: {full_kelly:.2f}, التقلب المتوقع: {predicted_vol:.4f})")
        return float(np.clip(allocated_capital, 0.0, capital * 0.10)) # بحد أقصى 10% من رأس المال لكل صفقة
