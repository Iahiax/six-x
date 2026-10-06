import numpy as np
from typing import Tuple, Dict, Any

class EconomicSurpriseMacroEngine:
    def __init__(self, gamma: float = 1.5):
        self.gamma = gamma

    def calculate_z_surprise(self, actual: float, consensus: float, historical_std: float) -> float:
        if historical_std <= 0:
            return 0.0
        return float((actual - consensus) / historical_std)

    def evaluate_news_blackout(self, event_z_score: float) -> Tuple[bool, str]:
        if abs(event_z_score) >= 2.5:
            return True, f"BLACKOUT_HIGH_IMPACT_SURPRISE (Z-Score: {event_z_score:.2f})"
        return False, "CLEAR"

    def convert_sentiment_to_scalar(self, raw_sentiment_score: float) -> float:
        sigmoid_val = 1.0 / (1.0 + np.exp(-self.gamma * raw_sentiment_score))
        return float(2.0 * sigmoid_val - 1.0)
