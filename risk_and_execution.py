import requests
import logging
from config import config
from state_persistence import SystemStateManager

logger = logging.getLogger("RiskExecution")

class RiskAndExecutionEngine:
    """
    محرك إدارة المخاطر والتنفيذ المباشر للأوامر
    يتضمن قاطع التيار (Circuit Breaker)، التحقق من الانزلاق السعري (Slippage)، وحظر تداول فترة تثبيت لندن.
    """
    def __init__(self, state_mgr: SystemStateManager):
        self.state_mgr = state_mgr
        self.is_circuit_broken = False

    def check_london_fix_restriction(self, current_utc_hour: int, current_utc_minute: int) -> bool:
        """حظر التداول التلقائي بين الساعة 15:55 و 16:05 UTC (London 4PM Fix)"""
        if current_utc_hour == 15 and current_utc_minute >= 55:
            return True
        if current_utc_hour == 16 and current_utc_minute <= 5:
            return True
        return False

    def validate_slippage(self, expected_price: float, current_price: float) -> bool:
        """التحقق من عدم تجاوز الانزلاق السعري للحد المسموح"""
        slippage = abs(current_price - expected_price)
        if slippage > config.MAX_SLIPPAGE_POINTS:
            logger.warning(f"[Slippage Alert]: الانزلاق السعري ({slippage:.2f}) تجاوز الحد المسموح ({config.MAX_SLIPPAGE_POINTS})")
            return False
        return True

    def trigger_circuit_breaker(self, reason: str):
        """تجميد التداول وتفعيل قاطع التيار الطارئ"""
        self.is_circuit_broken = True
        logger.critical(f"[CIRCUIT BREAKER TRIGGERED]: {reason}")
        self.state_mgr.add_log("CRITICAL", f"Circuit Breaker Triggered: {reason}")

    def execute_order(self, epic: str, direction: str, size: float, current_price: float, expected_price: float) -> dict:
        """تنفيذ أمر تداول حقيقي مع فحص معايير الحماية والأمان"""
        if self.is_circuit_broken:
            return {"status": "REJECTED", "reason": "Circuit breaker is ACTIVE"}

        if not self.validate_slippage(expected_price, current_price):
            return {"status": "REJECTED", "reason": "Slippage threshold exceeded"}

        # بناء جسم الطلب لمنصة Capital.com
        payload = {
            "epic": epic,
            "direction": direction,
            "size": size,
            "orderType": "MARKET",
            "guaranteedStop": False
        }
        
        headers = {
            "X-CAP-API-KEY": config.CAPITAL_API_KEY,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{config.CAPITAL_API_URL}/positions",
                json=payload,
                headers=headers,
                timeout=5
            )
            data = response.json()
            if response.status_code == 200 and "dealReference" in data:
                deal_id = data.get("dealReference")
                self.state_mgr.log_trade(deal_id, epic, direction, size, current_price)
                return {"status": "SUCCESS", "deal_id": deal_id}
            else:
                return {"status": "FAILED", "reason": data.get("errorCode", "Unknown API error")}
        except Exception as e:
            logger.error(f"[Execution Error]: {e}")
            return {"status": "ERROR", "reason": str(e)}
