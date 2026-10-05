import requests
import logging
from typing import Dict, List, Any
from config import config

logger = logging.getLogger("MarketUniverse")

class CapitalMarketUniverse:
    """
    محرك جلب كافة الأسهم والأصول المتاحة على Capital.com ديناميكياً
    """
    def __init__(self):
        self.base_url = config.CAPITAL_API_URL
        self.headers = {
            "X-CAP-API-KEY": config.CAPITAL_API_KEY,
            "Content-Type": "application/json"
        }
        self.universe: Dict[str, Dict[str, Any]] = {}

    def fetch_all_categories(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.base_url}/marketnavigation", headers=self.headers, timeout=10)
            if res.status_code == 200:
                return res.json().get("nodes", [])
            return []
        except Exception as e:
            logger.error(f"فشل جلب شجرة السوق: {e}")
            return []

    def scan_full_universe(self, search_term: str = "") -> Dict[str, Dict[str, Any]]:
        endpoint = f"{self.base_url}/markets"
        params = {"searchTerm": search_term} if search_term else {}
        
        try:
            res = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if res.status_code == 200:
                markets = res.json().get("markets", [])
                for mkt in markets:
                    epic = mkt.get("epic")
                    self.universe[epic] = {
                        "instrument_name": mkt.get("instrumentName"),
                        "instrument_type": mkt.get("instrumentType"),
                        "min_size": mkt.get("minDealSize", 0.1),
                        "max_leverage": mkt.get("maxLeverage", 1.0),
                        "tick_size": mkt.get("tickSize", 0.01),
                        "currency": mkt.get("currency", "USD"),
                        "market_status": mkt.get("marketStatus")
                    }
                logger.info(f"تم اكتشاف وتحديث {len(self.universe)} أداة مالية.")
            return self.universe
        except Exception as e:
            logger.error(f"خطأ أثناء مسح الأصول: {e}")
            return {}

    def filter_assets_by_type(self, asset_type: str) -> List[str]:
        return [epic for epic, info in self.universe.items() if info["instrument_type"] == asset_type.upper()]
