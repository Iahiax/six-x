import numpy as np
import pandas as pd
from typing import Dict, List, Any

class InstitutionalPortfolioAllocator:
    """
    محرك توزيع رأس المال والمحفظة متعددة الأصول المتوافق مع شروط المخاطر المؤسسية
    """
    def __init__(self, total_capital: float = 100000.0, max_leverage: float = 2.0, max_asset_weight: float = 0.35):
        self.total_capital = total_capital
        self.max_leverage = max_leverage
        self.max_asset_weight = max_asset_weight

    def calculate_portfolio_allocations(
        self,
        symbols: List[str],
        returns_df: pd.DataFrame,
        signal_strengths: Dict[str, float], # إشارات النماذج (-1.0 إلى +1.0)
        macro_biases: Dict[str, float],     # انحياز العقل الاقتصادي لكل أصل
        volatilities: Dict[str, float]      # تقلبات GARCH/Historical
    ) -> Dict[str, Dict[str, float]]:
        """
        حساب توزيع رأس المال والحجم المخصص لكل أصل مالي مع مراعاة الارتباط والمخاطر
        """
        n_assets = len(symbols)
        if n_assets == 0:
            return {}

        # 1. مصفوفة التباين والارتباط المشترك (Covariance Matrix)
        cov_matrix = returns_df[symbols].cov().values if not returns_df.empty else np.eye(n_assets)

        # 2. حساب وزن توازن المخاطر العكسية (Inverse Volatility Weights)
        inv_vols = np.array([1.0 / max(volatilities.get(s, 0.02), 0.001) for s in symbols])
        risk_parity_weights = inv_vols / np.sum(inv_vols)

        # 3. تعديل الوزن بناءً على إشارة الذكاء الاصطناعي وانحياز الاقتصاد الكلي
        combined_signals = []
        for i, symbol in enumerate(symbols):
            sig = signal_strengths.get(symbol, 0.0)
            bias = macro_biases.get(symbol, 0.0)
            # النتيجة المدمجة: 60% إشارة النماذج + 40% العقل الاقتصادي
            combined_score = (0.6 * sig) + (0.4 * bias)
            combined_signals.append(combined_score)

        combined_signals = np.array(combined_signals)

        # 4. حساب Kelly Fractional Weight
        # $w_i = \frac{\mu_i}{\sigma_i^2} \times \text{Half-Kelly Fraction}$
        raw_weights = risk_parity_weights * combined_signals * 0.5

        # 5. تطبيق حدود المحفظة (Portfolio Constraints & Max Drawdown Caps)
        abs_weights = np.abs(raw_weights)
        total_exposure = np.sum(abs_weights)

        if total_exposure > self.max_leverage:
            raw_weights = (raw_weights / total_exposure) * self.max_leverage

        # تطبيق الحد الأقصى للأصل الواحد
        final_allocations = {}
        for i, symbol in enumerate(symbols):
            weight = np.clip(raw_weights[i], -self.max_asset_weight, self.max_asset_weight)
            allocated_usd = self.total_capital * weight

            final_allocations[symbol] = {
                "weight": float(weight),
                "allocated_capital_usd": float(allocated_usd),
                "direction": "BUY" if weight > 0.05 else ("SELL" if weight < -0.05 else "HOLD"),
                "risk_score": float(volatilities.get(symbol, 0.02))
            }

        return final_allocations
