import pandas as pd
import numpy as np
from massive_indicators import MassiveQuantIndicators

class StrategyMatrix:
    """
    مصفوفة تقييم الاستراتيجيات الكمية المتقدمة
    """
    @staticmethod
    def stat_arb_pairs_signal(series_a: pd.Series, series_b: pd.Series, z_threshold: float = 2.0) -> int:
        spread = series_a - series_b
        mean = spread.rolling(30).mean().iloc[-1]
        std = spread.rolling(30).std().iloc[-1]
        if std == 0 or np.isnan(std):
            return 1
        z_score = (spread.iloc[-1] - mean) / std
        if z_score > z_threshold:
            return 0 # Sell Asset A / Buy Asset B
        elif z_score < -z_threshold:
            return 2 # Buy Asset A / Sell Asset B
        return 1 # Hold

    @staticmethod
    def volatility_squeeze_breakout(df: pd.DataFrame) -> int:
        bb = MassiveQuantIndicators.bollinger_bands(df['close'])
        kc = MassiveQuantIndicators.keltner_channels(df)
        
        squeeze_on = (bb['lower'].iloc[-1] > kc['lower'].iloc[-1]) and (bb['upper'].iloc[-1] < kc['upper'].iloc[-1])
        
        if not squeeze_on:
            momentum = df['close'].iloc[-1] - df['close'].iloc[-20]
            if momentum > 0:
                return 2 # Buy
            elif momentum < 0:
                return 0 # Sell
        return 1 # Hold
