import numpy as np
import requests
from typing import Dict, Tuple, Any

class EconomicSurpriseMacroEngine:
    """
    محرك مفاجآت الأخبار: $Z_{surprise}$ والدالة السجمويدية لتعديل اتجاه الصفقات
    """
    def __init__(self, fmp_key: str = "", gamma: float = 1.5):
        self.fmp_key = fmp_key
        self.gamma = gamma

    def calculate_z_surprise(self, actual: float, consensus: float, historical_std: float) -> float:
        """
        حساب مؤشر المفاجأة الاقتصادية:
        $$Z_{surprise} = \frac{\text{Actual} - \text{Consensus}}{\sigma_{historical}}$$
        """
        if historical_std <= 0:
            return 0.0
        return float((actual - consensus) / historical_std)

    def evaluate_news_blackout(self, event_z_score: float) -> Tuple[bool, str]:
        """
        تفعيل درع التوقف الفوري عند الأخبار المفاجئة جداً
        """
        if abs(event_z_score) >= 2.5:
            return True, f"BLACKOUT_HIGH_IMPACT_SURPRISE (Z-Score: {event_z_score:.2f})"
        return False, "CLEAR"

    def convert_sentiment_to_scalar(self, raw_sentiment_score: float) -> float:
        """
        تحويل مشاعر الأخبار إلى معامل موحد بين $[-1.0, +1.0]$:
        $$M_{news} = 2 \cdot \left( \frac{1}{1 + e^{-\gamma \cdot S_{score}}} \right) - 1$$
        """
        sigmoid_val = 1.0 / (1.0 + np.exp(-self.gamma * raw_sentiment_score))
        return float(2.0 * sigmoid_val - 1.0)
