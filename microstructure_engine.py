import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class MarketTick:
    timestamp: float
    price: float
    volume: float
    bid: float
    ask: float
    bid_vol: float
    ask_vol: float

class MicrostructureQuantEngine:
    """
    محرك تحليل الميكروثانية: السعر الميكروي، VPIN بروتوكول Lee-Ready، ومحرك Hawkes Process
    """
    def __init__(self, bucket_volume: float = 10000.0, num_buckets: int = 50, theta: float = 0.5):
        self.bucket_volume = bucket_volume
        self.num_buckets = num_buckets
        self.theta = theta
        
        # حاويات VPIN
        self.current_bucket_buy_vol = 0.0
        self.current_bucket_sell_vol = 0.0
        self.current_bucket_filled = 0.0
        self.vpin_buckets: List[Tuple[float, float]] = []  # (Buy_Vol, Sell_Vol)
        
        # معاملات Hawkes Process
        self.mu_0 = 0.1       # معدل الوصول الورودي الأساسي
        self.alpha = 0.8      # قوة القفزة عند وصول أمر سام
        self.beta = 1.2       # معدل تلاشي التأثير
        self.event_times: List[float] = []

        self.last_price = 0.0

    def calculate_micro_price(self, tick: MarketTick, ofi_signal: float) -> float:
        """
        حساب السعر الميكروي المصحوب بضبط عدم التوازن:
        $$P_{micro} = P_{bid} \cdot \left(\frac{V_{ask}}{V_{bid} + V_{ask}}\right) + P_{ask} \cdot \left(\frac{V_{bid}}{V_{bid} + V_{ask}}\right) + \theta \cdot \text{Spread} \cdot \tanh(\text{OFI})$$
        """
        total_vol = tick.bid_vol + tick.ask_vol
        if total_vol <= 0:
            return (tick.bid + tick.ask) / 2.0
            
        spread = tick.ask - tick.bid
        raw_micro = (tick.bid * (tick.ask_vol / total_vol)) + (tick.ask * (tick.bid_vol / total_vol))
        ofi_adjustment = self.theta * spread * np.tanh(ofi_signal)
        
        return float(raw_micro + ofi_adjustment)

    def classify_trade_lee_ready(self, price: float, bid: float, ask: float) -> str:
        """
        تصنيف الصفقات بناءً على قاعدة Lee-Ready
        """
        mid_price = (bid + ask) / 2.0
        if price > mid_price:
            return "BUY"
        elif price < mid_price:
            return "SELL"
        else:
            # Tick Rule إذا كان السعر عند المنتصف تماماً
            if price >= self.last_price:
                return "BUY"
            else:
                return "SELL"

    def update_vpin(self, tick: MarketTick) -> float:
        """
        تحديث حاويات VPIN وحساب النسبة الكلية لسمية التدفق
        """
        trade_type = self.classify_trade_lee_ready(tick.price, tick.bid, tick.ask)
        self.last_price = tick.price
        
        remaining_vol = tick.volume
        while remaining_vol > 0:
            space_in_bucket = self.bucket_volume - self.current_bucket_filled
            fill_amount = min(remaining_vol, space_in_bucket)
            
            if trade_type == "BUY":
                self.current_bucket_buy_vol += fill_amount
            else:
                self.current_bucket_sell_vol += fill_amount
                
            self.current_bucket_filled += fill_amount
            remaining_vol -= fill_amount
            
            if self.current_bucket_filled >= self.bucket_volume:
                self.vpin_buckets.append((self.current_bucket_buy_vol, self.current_bucket_sell_vol))
                if len(self.vpin_buckets) > self.num_buckets:
                    self.vpin_buckets.pop(0)
                
                # إعادة ضبط الحاوية
                self.current_bucket_buy_vol = 0.0
                self.current_bucket_sell_vol = 0.0
                self.current_bucket_filled = 0.0

        if not self.vpin_buckets:
            return 0.0

        # $$VPIN = \frac{\sum |V^B - V^S|}{N \times V}$$
        total_imbalance = sum(abs(b - s) for b, s in self.vpin_buckets)
        vpin = total_imbalance / (len(self.vpin_buckets) * self.bucket_volume)
        return float(vpin)

    def compute_hawkes_intensity(self, current_time: float) -> Tuple[float, bool]:
        """
        حساب كثافة Hawkes Process للتحذير من الانهيارات المفاجئة
        $$\lambda(t) = \mu_0 + \sum_{t_i < t} \alpha \cdot e^{-\beta (t - t_i)}$$
        """
        self.event_times.append(current_time)
        # الاحتفاظ بالأحداث خلال نافذة زمنية قدرها 60 ثانية
        self.event_times = [t for t in self.event_times if current_time - t <= 60.0]
        
        intensity = self.mu_0
        for t_i in self.event_times[:-1]:
            intensity += self.alpha * np.exp(-self.beta * (current_time - t_i))
            
        branching_ratio = self.alpha / self.beta
        is_toxic_crash_imminent = (branching_ratio >= 0.95) and (intensity > 5.0)
        
        return float(intensity), is_toxic_crash_imminent
