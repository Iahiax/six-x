import os
import time
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("BrokerClient")

class CapitalComClient:
    """
    عميل الاتصال التفاعلي معCapital.com REST API
    """
    def __init__(self, api_key: str = "", identifier: str = "", password: str = "", is_demo: bool = True):
        self.api_key = api_key or os.getenv("CAPITAL_API_KEY", "")
        self.identifier = identifier or os.getenv("CAPITAL_IDENTIFIER", "")
        self.password = password or os.getenv("CAPITAL_PASSWORD", "")
        
        self.base_url = "https://demo-api-capital.backend-capital.com/api/v1" if is_demo else "https://api-capital.backend-capital.com/api/v1"
        self.cst = ""
        self.security_token = ""
        self.active_account_id = ""

    def create_session(self) -> bool:
        """
        إنشاء جلسة تداول جديدة وجلب توكنات الأمان CST و X-SECURITY-TOKEN
        """
        url = f"{self.base_url}/session"
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "identifier": self.identifier,
            "password": self.password
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                self.cst = response.headers.get("CST", "")
                self.security_token = response.headers.get("X-SECURITY-TOKEN", "")
                data = response.json()
                self.active_account_id = data.get("currentAccountId", "")
                logger.info("✅ تم إنشاء جلسة Capital.com بنجاح.")
                return True
            else:
                logger.error(f"❌ فشل إنشاء الجلسة: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال بـ Capital.com: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.security_token,
            "Content-Type": "application/json"
        }

    def get_market_quote(self, epic: str) -> Optional[Dict[str, Any]]:
        """
        جلب أسعار العرض والطلب الحية لرمز معين (e.g. 'NVDA', 'EURUSD', 'BTCUSD')
        """
        url = f"{self.base_url}/markets/{epic}"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=5)
            if res.status_code == 200:
                snapshot = res.json().get("snapshot", {})
                return {
                    "epic": epic,
                    "bid": float(snapshot.get("bid", 0.0)),
                    "ask": float(snapshot.get("offer", 0.0)),
                    "high": float(snapshot.get("high", 0.0)),
                    "low": float(snapshot.get("low", 0.0)),
                    "marketStatus": snapshot.get("marketStatus", "CLOSED")
                }
            elif res.status_code == 401:
                # تجديد الجلسة عند انتهاء الصلاحية
                if self.create_session():
                    return self.get_market_quote(epic)
        except Exception as e:
            logger.error(f"خطأ عند جلب أسعار {epic}: {e}")
        return None

    def execute_order(self, epic: str, direction: str, size: float, stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Dict[str, Any]:
        """
        تنفيذ أمر تداول مباشر (BUY / SELL)
        """
        url = f"{self.base_url}/positions"
        payload = {
            "epic": epic,
            "direction": direction.upper(),
            "size": abs(size),
            "guaranteedStop": False
        }
        if stop_loss:
            payload["stopLevel"] = stop_loss
        if take_profit:
            payload["profitLevel"] = take_profit

        try:
            res = requests.post(url, json=payload, headers=self._get_headers(), timeout=5)
            if res.status_code == 200:
                return {"status": "SUCCESS", "dealReference": res.json().get("dealReference")}
            else:
                return {"status": "FAILED", "error": res.text}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
