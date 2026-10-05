import numpy as np
import pandas as pd

class MassiveQuantIndicators:
    """
    المكتبة الحاسوبية الشاملة للمؤشرات الفنية والإحصائية
    """
    @staticmethod
    def ema(series: pd.Series, period: int = 14) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        high, low, close = df['high'], df['low'], df['close']
        atr = MassiveQuantIndicators.atr(df, period)
        hl2 = (high + low) / 2
        basic_upper = hl2 + (multiplier * atr)
        basic_lower = hl2 - (multiplier * atr)
        
        upper_band = pd.Series(0.0, index=df.index)
        lower_band = pd.Series(0.0, index=df.index)
        trend = pd.Series(1, index=df.index)

        for i in range(1, len(df)):
            upper_band.iloc[i] = basic_upper.iloc[i] if basic_upper.iloc[i] < upper_band.iloc[i-1] or close.iloc[i-1] > upper_band.iloc[i-1] else upper_band.iloc[i-1]
            lower_band.iloc[i] = basic_lower.iloc[i] if basic_lower.iloc[i] > lower_band.iloc[i-1] or close.iloc[i-1] < lower_band.iloc[i-1] else lower_band.iloc[i-1]
            
            if close.iloc[i] > upper_band.iloc[i-1]:
                trend.iloc[i] = 1
            elif close.iloc[i] < lower_band.iloc[i-1]:
                trend.iloc[i] = -1
            else:
                trend.iloc[i] = trend.iloc[i-1]

        return pd.DataFrame({'supertrend': np.where(trend == 1, lower_band, upper_band), 'trend': trend})

    @staticmethod
    def ichimoku_cloud(df: pd.DataFrame) -> pd.DataFrame:
        high, low = df['high'], df['low']
        tenkan_sen = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun_sen = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        senkou_span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        chikou_span = df['close'].shift(-26)
        return pd.DataFrame({
            'tenkan_sen': tenkan_sen, 'kijun_sen': kijun_sen,
            'senkou_a': senkou_span_a, 'senkou_b': senkou_span_b, 'chikou': chikou_span
        })

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def stochastic_oscillator(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        low_min = df['low'].rolling(k_period).min()
        high_max = df['high'].rolling(k_period).max()
        stoch_k = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-9))
        stoch_d = stoch_k.rolling(d_period).mean()
        return pd.DataFrame({'stoch_k': stoch_k, 'stoch_d': stoch_d})

    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        fast_ema = series.ewm(span=fast, adjust=False).mean()
        slow_ema = series.ewm(span=slow, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return pd.DataFrame({'macd': macd_line, 'signal': signal_line, 'hist': histogram})

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    @staticmethod
    def bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        sma = series.rolling(period).mean()
        std = series.rolling(period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        bandwidth = (upper - lower) / (sma + 1e-9)
        return pd.DataFrame({'middle': sma, 'upper': upper, 'lower': lower, 'bandwidth': bandwidth})

    @staticmethod
    def keltner_channels(df: pd.DataFrame, period: int = 20, atr_mult: float = 2.0) -> pd.DataFrame:
        middle = df['close'].ewm(span=period, adjust=False).mean()
        atr_val = MassiveQuantIndicators.atr(df, period)
        upper = middle + (atr_mult * atr_val)
        lower = middle - (atr_mult * atr_val)
        return pd.DataFrame({'middle': middle, 'upper': upper, 'lower': lower})

    @staticmethod
    def garman_klass_volatility(df: pd.DataFrame, period: int = 20) -> pd.Series:
        log_hl = np.log(df['high'] / (df['low'] + 1e-9)) ** 2
        log_co = np.log(df['close'] / (df['open'] + 1e-9)) ** 2
        rs = 0.5 * log_hl - (2 * np.log(2) - 1) * log_co
        return np.sqrt(rs.rolling(period).mean())

    @staticmethod
    def vwap(df: pd.DataFrame) -> pd.Series:
        tp = (df['high'] + df['low'] + df['close']) / 3
        return (tp * df['volume']).cumsum() / (df['volume'].cumsum() + 1e-9)

    @staticmethod
    def kalman_filter_smooth(prices: np.ndarray) -> np.ndarray:
        n = len(prices)
        if n == 0:
            return np.array([])
        xhat = np.zeros(n)
        P = np.zeros(n)
        xhatminus = np.zeros(n)
        Pminus = np.zeros(n)
        K = np.zeros(n)
        Q = 1e-5
        R = 0.01 ** 2
        xhat[0] = prices[0]
        P[0] = 1.0

        for k in range(1, n):
            xhatminus[k] = xhat[k-1]
            Pminus[k] = P[k-1] + Q
            K[k] = Pminus[k] / (Pminus[k] + R)
            xhat[k] = xhatminus[k] + K[k] * (prices[k] - xhatminus[k])
            P[k] = (1 - K[k]) * Pminus[k]
        return xhat
