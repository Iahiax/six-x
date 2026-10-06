import os
import json
import time
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("BrokerClient")

class CapitalComClient:
    """
    عميل الاتصال التفاعلي المتقدم مع Capital.com REST API
    """
    def __init__(
        self,
        api_key: str = "",
        identifier: str = "",
        password: str = "",
        is_demo: bool = True
    ):
        # الاعتماد على المتغيرات الممررة أو الجلب التلقائي من المتغيرات البيئية
        self.api_key = api_key or os.getenv("CAPITAL_API_KEY", "ut2RpxSbx6fiDdHv")
        self.identifier = identifier or os.getenv("CAPITAL_IDENTIFIER", "yahia.x@outlook.sa")
        self.password = password or os.getenv("CAPITAL_PASSWORD", "Yahia@1411")
        self.is_demo = is_demo
        
        self.server = "https://demo-api-capital.backend-capital.com" if self.is_demo else "https://api-capital.backend-capital.com"
        self.cst = ""
        self.xst = ""
        self.active_account_id = ""

    def create_session(self) -> bool:
        """
        تسجيل الدخول وجلب توكنات الأمان CST و X-SECURITY-TOKEN
        """
        url = f"{self.server}/api/v1/session"
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "identifier": self.identifier,
            "password": self.password,
            "encryptedPassword": False
        }

        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            
            if res.status_code == 200:
                self.cst = res.headers.get("CST", "")
                self.xst = res.headers.get("X-SECURITY-TOKEN", "")
                data = res.json()
                self.active_account_id = data.get("currentAccountId", "")
                logger.info(f"✅ تم تسجيل الدخول بنجاح. CST/XST Generated. Account ID: {self.active_account_id}")
                return True
            else:
                logger.error(f"❌ فشل تسجيل الدخول ({res.status_code}): {res.text}")
                return False
        except Exception as e:
            logger.error(f"❌ خطأ أثناء الاتصال بالخادم: {e}")
            return False

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        توليد الهيدرز المتضمنة توكنات الجلسة للطلبات التالية
        """
        return {
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.xst,
            "Content-Type": "application/json"
        }

    def get_market_quote(self, epic: str) -> Optional[Dict[str, Any]]:
        """
        جلب أسعار العرض والطلب المباشرة لرمز معين
        """
        if not self.cst or not self.xst:
            if not self.create_session():
                return None

        url = f"{self.server}/api/v1/markets/{epic}"
        try:
            res = requests.get(url, headers=self._get_auth_headers(), timeout=5)
            
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
                logger.warning("🔄 انتهت صلاحية الجلسة، جاري إعادة تسجيل الدخول...")
                if self.create_session():
                    return self.get_market_quote(epic)
            else:
                logger.error(f"خطأ في جلب سعر {epic}: {res.status_code} - {res.text}")
        except Exception as e:
            logger.error(f"خطأ في طلب الأسعار لـ {epic}: {e}")
            
        return None

    def execute_order(
        self, 
        epic: str, 
        direction: str, 
        size: float, 
        stop_loss: Optional[float] = None, 
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        تنفيذ أمر تداول مباشر (BUY / SELL)
        """
        if not self.cst or not self.xst:
            if not self.create_session():
                return {"status": "ERROR", "message": "فشل إنشاء الجلسة"}

        url = f"{self.server}/api/v1/positions"
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
            res = requests.post(url, headers=self._get_auth_headers(), data=json.dumps(payload), timeout=5)
            
            if res.status_code == 200:
                deal_ref = res.json().get("dealReference", "")
                logger.info(f"✅ تم تنفيذ الصفقة بنجاح. Deal Ref: {deal_ref}")
                return {"status": "SUCCESS", "dealReference": deal_ref}
            elif res.status_code == 401:
                if self.create_session():
                    return self.execute_order(epic, direction, size, stop_loss, take_profit)
            else:
                logger.error(f"❌ فشل تنفيذ الصفقة: {res.status_code} - {res.text}")
                return {"status": "FAILED", "error": res.text}
        except Exception as e:
            logger.error(f"❌ استثناء أثناء تنفيذ الصفقة: {e}")
            return {"status": "ERROR", "message": str(e)}

        return {"status": "FAILED", "error": "Unknown Error"}
