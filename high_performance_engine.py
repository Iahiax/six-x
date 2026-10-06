import polars as pl
import numpy as np
import logging

logger = logging.getLogger("HighPerfEngine")

class MicrostructureQuantEngine:
    """
    محرك معالجة بيانات الميكروثانية وحساب Order Flow Imbalance (OFI)
    """
    @staticmethod
    def calculate_ofi(bid_prices: np.ndarray, bid_volumes: np.ndarray, 
                      ask_prices: np.ndarray, ask_volumes: np.ndarray) -> float:
        """
        حساب عدم التوازن في تدفق الأوامر (Order Flow Imbalance) بناءً على حركة دفتر الأوامر Level 2
        """
        if len(bid_prices) < 2 or len(ask_prices) < 2:
            return 0.0

        # التغير في أسعار وأحجام العرض والطلب
        delta_bid_price = bid_prices[-1] - bid_prices[-2]
        delta_ask_price = ask_prices[-1] - ask_prices[-2]

        # حساب تدفق الطلب (Bid Demand Flow)
        if delta_bid_price > 0:
            e_bid = bid_volumes[-1]
        elif delta_bid_price == 0:
            e_bid = bid_volumes[-1] - bid_volumes[-2]
        else:
            e_bid = 0.0

        # حساب تدفق العرض (Ask Supply Flow)
        if delta_ask_price < 0:
            e_ask = ask_volumes[-1]
        elif delta_ask_price == 0:
            e_ask = ask_volumes[-1] - ask_volumes[-2]
        else:
            e_ask = 0.0

        # صافي تدفق الأوامر (OFI)
        ofi = e_bid - e_ask
        return float(ofi)

    @staticmethod
    def fast_polars_indicators(prices_list: list) -> dict:
        """
        حساب المائة مؤشر وسلسلة العوائد بسرعة محرك Rust/Polars
        """
        df = pl.DataFrame({"close": prices_list})
        df = df.with_columns([
            pl.col("close").pct_change().alias("returns"),
            pl.col("close").ewm_mean(span=14).alias("ema_14"),
            pl.col("close").std(length=20).alias("volatility_20")
        ])

        latest = df.tail(1).to_dicts()[0]
        return {
            "returns": latest["returns"] if latest["returns"] is not None else 0.0,
            "ema_14": latest["ema_14"] if latest["ema_14"] is not None else prices_list[-1],
            "volatility": latest["volatility_20"] if latest["volatility_20"] is not None else 0.0
        }
