import zoneinfo
from datetime import datetime, time, timedelta
from typing import Tuple, Dict, Any

class AdvancedMarketSessionTimer:
    """
    مُحيّد الجلسات ومؤقت الأسواق اللحظي مع دعم التوقيت الصيفي والعد التنازلي
    """
    def __init__(self):
        self.ny_tz = zoneinfo.ZoneInfo("America/New_York")
        self.utc_tz = zoneinfo.ZoneInfo("UTC")

    def get_market_status(self, asset_type: str) -> Tuple[bool, str, int]:
        """
        إرجاع: (هل السوق مفتوح؟، وصف الحالة، الثواني المتبقية حتى التغير القادم)
        """
        now_utc = datetime.now(self.utc_tz)
        now_ny = datetime.now(self.ny_tz)

        if asset_type == "CRYPTO":
            return True, "CRYPTO_ALWAYS_OPEN_247", 86400

        elif asset_type == "FOREX":
            weekday = now_utc.weekday() # 0 = Mon, 6 = Sun
            hour = now_utc.hour

            if weekday == 5 or (weekday == 4 and hour >= 22) or (weekday == 6 and hour < 22):
                # حساب موعد الافتتاح الأحد 22:00 UTC
                days_until_sun = (6 - weekday) % 7
                target_open = (now_utc + timedelta(days=days_until_sun)).replace(hour=22, minute=0, second=0, microsecond=0)
                seconds_left = int((target_open - now_utc).total_seconds())
                return False, "FOREX_WEEKEND_CLOSED", max(seconds_left, 0)
            else:
                return True, "FOREX_MARKET_OPEN", 3600

        elif asset_type == "US_EQUITIES":
            weekday = now_ny.weekday()
            current_time = now_ny.time()
            
            open_time = time(9, 30, 0)
            close_time = time(16, 0, 0)

            if weekday >= 5:
                days_to_mon = 7 - weekday
                next_mon = (now_ny + timedelta(days=days_to_mon)).replace(hour=9, minute=30, second=0, microsecond=0)
                return False, "EQUITIES_WEEKEND_CLOSED", int((next_mon - now_ny).total_seconds())

            if current_time < open_time:
                next_open = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
                return False, "EQUITIES_PRE_MARKET_CLOSED", int((next_open - now_ny).total_seconds())
            elif current_time >= close_time:
                next_day = (now_ny + timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0)
                if next_day.weekday() >= 5:
                    next_day += timedelta(days=(7 - next_day.weekday()))
                return False, "EQUITIES_POST_MARKET_CLOSED", int((next_day - now_ny).total_seconds())
            else:
                next_close = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)
                return True, "EQUITIES_REGULAR_SESSION_OPEN", int((next_close - now_ny).total_seconds())

        return True, "UNKNOWN_ASSET_OPEN", 3600
