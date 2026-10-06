import os
import requests
import logging

logger = logging.getLogger("TelegramAlerts")

class TelegramNotifier:
    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")

    def send_notification(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("تنبيه: لم يتم ضبط بيانات Telegram Bot.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة التليجرام: {e}")
            return False
