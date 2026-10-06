import pytz
from datetime import datetime, time, timedelta
from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger("MarketSessionEngine")

class MarketSessionTimer:
    """
    محرك إدارة أوقات الجلسات ومؤقت التوقف والاستئناف التلقائي بحسب نوع الأصل المالي
    """
    def __init__(self):
        self.utc = pytz.utc
        self.ny_tz = pytz.timezone("America/New_York")

    def is_market_open(self, asset_class: str = "US_EQUITIES") -> Tuple[bool, str, int]:
        """
        التحقق من حالة السوق.
        المرجعات: (هل السوق مفتوح؟، اسم الجلسة/الحالة، الثواني المتبقية حتى التغير القادم)
        """
        now_utc = datetime.now(self.utc)
        now_ny = now_utc.astimezone(self.ny_tz)

        if asset_class == "CRYPTO":
            # سوق العملات الرقمية مفتوح 24/7
            return True, "CRYPTO_247", 86400

        elif asset_class == "FOREX":
            # سوق العملات (Forex): يفتح الأحد 22:00 UTC ويغلق الجمعة 22:00 UTC
            weekday = now_utc.weekday() # 0 = Monday, ..., 6 = Sunday
            hour = now_utc.hour

            if weekday == 5: # Saturday
                # حساب الوقت المتبقي حتى افتتاح الأحد 22:00 UTC
                next_open = (now_utc + timedelta(days=(6 - weekday))).replace(hour=22, minute=0, second=0, microsecond=0)
                seconds_left = int((next_open - now_utc).total_seconds())
                return False, "FOREX_WEEKEND_CLOSED", seconds_left
            elif weekday == 4 and hour >= 22: # Friday after 22:00 UTC
                next_open = (now_utc + timedelta(days=2)).replace(hour=22, minute=0, second=0, microsecond=0)
                seconds_left = int((next_open - now_utc).total_seconds())
                return False, "FOREX_WEEKEND_CLOSED", seconds_left
            elif weekday == 6 and hour < 22: # Sunday before 22:00 UTC
                next_open = now_utc.replace(hour=22, minute=0, second=0, microsecond=0)
                seconds_left = int((next_open - now_utc).total_seconds())
                return False, "FOREX_WEEKEND_CLOSED", seconds_left
            else:
                # تحديد الجلسة النشطة
                session = "FOREX_ACTIVE_"
                if 0 <= hour < 9: session += "TOKYO"
                elif 7 <= hour < 16: session += "LONDON"
                else: session += "NEW_YORK"
                return True, session, 3600

        elif asset_class == "US_EQUITIES":
            # الأسهم الأمريكية: الإثنين - الجمعة 09:30 AM - 04:00 PM EST
            weekday = now_ny.weekday()
            current_time = now_ny.time()

            market_open = time(9, 30, 0)
            market_close = time(16, 0, 0)

            if weekday >= 5: # العطلة الأسبوعية
                days_until_monday = (7 - weekday) % 7
                next_open_date = (now_ny + timedelta(days=days_until_monday)).date()
                next_open = self.ny_tz.localize(datetime.combine(next_open_date, market_open))
                return False, "EQUITIES_WEEKEND_CLOSED", int((next_open - now_ny).total_seconds())

            if current_time < market_open:
                next_open = self.ny_tz.localize(datetime.combine(now_ny.date(), market_open))
                return False, "EQUITIES_PRE_MARKET_CLOSED", int((next_open - now_ny).total_seconds())
            elif current_time >= market_close:
                # موعد الافتتاح لليوم التالي
                next_day = now_ny.date() + timedelta(days=1)
                if next_day.weekday() >= 5: # إذا كان اليوم التالي عطلة
                    next_day += timedelta(days=(7 - next_day.weekday()))
                next_open = self.ny_tz.localize(datetime.combine(next_day, market_open))
                return False, "EQUITIES_POST_MARKET_CLOSED", int((next_open - now_ny).total_seconds())
            else:
                next_close = self.ny_tz.localize(datetime.combine(now_ny.date(), market_close))
                return True, "US_EQUITIES_REGULAR_SESSION", int((next_close - now_ny).total_seconds())

        return True, "UNKNOWN_ASSET_DEFAULT_OPEN", 3600
