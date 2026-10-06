import os
import requests
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

logger = logging.getLogger("MacroNewsBrain")

class MacroEconomicBrain:
    """
    العقل الاقتصادي الكلي: يربط بيانات FRED، FMP، و Finnhub لتحليل البيئة الاقتصادية الشاملة
    """
    def __init__(self):
        self.fred_key = os.getenv("FRED_API_KEY", "d295bdec801d4faf6f55e5a5ea34eb07")
        self.fmp_key = os.getenv("FMP_API_KEY", "Jh4bsnzdHnXSVvou5ehHKBbffdrEfrYa")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY", "d96hs19r01qr77dkhss0d96hs19r01qr77dkhssg")

    def fetch_fred_macro_indicators(self) -> Dict[str, float]:
        """
        جلب أهم المتغيرات الاقتصادية الكلية من البنك الفيدرالي (FRED)
        """
        indicators = {
            "FEDFUNDS": "Interest_Rate",      # أسعار الفائدة الأمريكية
            "T10Y2Y": "Yield_Curve_Inversion",# منحنى العائد (مؤشر الركود)
            "CPIAUCSL": "Inflation_CPI",      # مؤشر أسعار المستهلك
            "UNRATE": "Unemployment_Rate"     # معدل البطالة
        }
        data = {}
        for series_id, name in indicators.items():
            try:
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={self.fred_key}&file_type=json&sort_order=desc&limit=1"
                resp = requests.get(url, timeout=5).json()
                val = float(resp["observations"][0]["value"])
                data[name] = val
            except Exception as e:
                logger.error(f"خطأ في جلب مؤشر FRED {series_id}: {e}")
                data[name] = 0.0

        return data

    def check_economic_calendar_blackout(self, buffer_minutes: int = 30) -> Tuple[bool, str]:
        """
        درع الأخبار: التحقق مما إذا كان هناك خبر اقتصادي عالي التأثير (FOMC, CPI, NFP) قريب لتعليق التداول
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={self.fmp_key}"
            response = requests.get(url, timeout=5).json()

            now = datetime.utcnow()
            high_impact_events = ["CPI", "FOMC", "Non Farm Payrolls", "Fed Interest Rate Decision"]

            for event in response:
                event_name = event.get("event", "")
                impact = event.get("impact", "")
                event_date_str = event.get("date", "")

                if impact == "High" or any(h.lower() in event_name.lower() for h in high_impact_events):
                    event_time = datetime.strptime(event_date_str, "%Y-%m-%d %H:%M:%S")
                    diff_minutes = abs((event_time - now).total_seconds()) / 60.0

                    if diff_minutes <= buffer_minutes:
                        logger.warning(f"🚨 تفعيل درع حظر التداول! خبر عالي التأثير قريب: {event_name}")
                        return True, event_name

        except Exception as e:
            logger.error(f"خطأ في قراءة التقويم الاقتصادي من FMP: {e}")

        return False, "Clear"

    def fetch_finnhub_market_sentiment(self) -> Dict[str, Any]:
        """
        جلب مشاعر الأخبار الحية وتحليل اتجاه السياسة النقدية من Finnhub
        """
        try:
            url = f"https://finnhub.io/api/v1/news?category=general&token={self.finnhub_key}"
            news_items = requests.get(url, timeout=5).json()

            bullish_keywords = ["growth", "surge", "rally", "rate cut", "bullish", "easing"]
            bearish_keywords = ["inflation", "recession", "rate hike", "crash", "bearish", "war"]

            score = 0
            for item in news_items[:15]:
                headline = item.get("headline", "").lower()
                score += sum(1 for w in bullish_keywords if w in headline)
                score -= sum(1 for w in bearish_keywords if w in headline)

            normalized_sentiment = np.clip(score / 10.0, -1.0, 1.0)
            return {"news_sentiment_score": float(normalized_sentiment), "total_news_analyzed": len(news_items)}

        except Exception as e:
            logger.error(f"خطأ في جلب أخبار Finnhub: {e}")
            return {"news_sentiment_score": 0.0, "total_news_analyzed": 0}

    def evaluate_macro_regime(() -> Dict[str, Any]:
        """
        تكامل العقل الاقتصادي: دمج الاقتصاد الكلي + مشاعر الأخبار + فلاتر السلامة
        """
        fred_data = self.fetch_fred_macro_indicators()
        is_blackout, event_cause = self.check_economic_calendar_blackout()
        sentiment = self.fetch_finnhub_market_sentiment()

        # تحديد النظام الاقتصادي الكلي (Macro Regime Classification)
        yield_spread = fred_data.get("Yield_Curve_Inversion", 0.0)
        cpi = fred_data.get("Inflation_CPI", 0.0)

        if yield_spread < 0:
            regime = "RECESSION_WARNING_INVERTED_YIELD"
            regime_bias = -0.5
        elif cpi > 3.5:
            regime = "HIGH_INFLATION_HAWKISH"
            regime_bias = -0.3
        else:
            regime = "GOLDILOCKS_EXPANSION"
            regime_bias = 0.4

        # معادلة انحياز العقل الاقتصادي الموحد:
        # $MacroBias = 0.6 \times Sentiment + 0.4 \times RegimeBias$
        final_macro_bias = np.clip((0.6 * sentiment["news_sentiment_score"]) + (0.4 * regime_bias), -1.0, 1.0)

        return {
            "macro_bias": float(final_macro_bias),
            "regime": regime,
            "blackout_active": is_blackout,
            "blackout_cause": event_cause,
            "fred_metrics": fred_data,
            "news_sentiment": sentiment["news_sentiment_score"]
        }
