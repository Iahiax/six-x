import numpy as np
import pandas as pd

class DeepAlphaEnsemble:
    """
    محرك التعلم الآلي لاستخراج معالم الألفا وتوليد الإشارات التجميعية
    """
    @staticmethod
    def extract_features(df: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(index=df.index)
        features['returns'] = df['close'].pct_change()
        features['volatility_log'] = np.log(df['high'] / (df['low'] + 1e-9))
        features['volume_ratio'] = df['volume'] / (df['volume'].rolling(20).mean() + 1e-9)
        features['rsi_diff'] = df['close'].diff(1)
        return features.fillna(0)

    def predict_alpha_signal(self, features: pd.DataFrame) -> float:
        if features.empty:
            return 0.5
        last_vector = features.iloc[-1].to_numpy()
        raw_score = np.dot(last_vector, np.ones(len(last_vector))) / len(last_vector)
        probability = 1.0 / (1.0 + np.exp(-raw_score))
        return float(probability)
