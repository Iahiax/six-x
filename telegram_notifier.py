import requests
import logging
from typing import Dict, Any

logger = logging.getLogger("TelegramNotifier")

class TelegramNotifier:
    """
    محرّك إرسال التنبيهات الفورية عبر بوت Telegram
    """
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("لم يتم ضبط بيانات Telegram (TELEGRAM_BOT_TOKEN / CHAT_ID). تم تجاوز الإرسال.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        try:
            res = requests.post(self.api_url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"خطأ الاتصال بـ Telegram API: {e}")
            return False

    def notify_trade_signal(self, symbol: str, action: str, price: float, rsi: float, trend: str, strategy: str):
        emoji = "🟢" if action == "BUY" else ("🔴" if action == "SELL" else "🟡")
        message = (
            f"<b>{emoji} إشارة تداول جديدة [{action}]</b>\n\n"
            f"<b>الأصل:</b> <code>{symbol}</code>\n"
            f"<b>السعر الحالي:</b> <code>{price:.4f}</code>\n"
            f"<b>الاتجاه:</b> {trend.upper()}\n"
            f"<b>مؤشر RSI:</b> <code>{rsi:.2f}</code>\n"
            f"<b>الاستراتيجية:</b> <code>{strategy}</code>\n"
            f"----------------------------------\n"
            f"<i>تنبيه آلي صادر من النظام المؤسسي.</i>"
        )
        self.send_message(message)

    def notify_macro_economic_news(self, news_summary: str, impact_score: float):
        sentiment = "إيجابي حاد 📈" if impact_score > 0.3 else ("سلبي حاد 📉" if impact_score < -0.3 else "محايد ⚖️")
        message = (
            f"<b>🌐 تحليل خبر اقتصادي كلي</b>\n\n"
            f"<b>ملخص الخبر:</b> {news_summary}\n"
            f"<b>معامل التأثير:</b> <code>{impact_score:.2f}</code>\n"
            f"<b>تقييم السوق:</b> {sentiment}\n"
        )
        self.send_message(message)

    def notify_portfolio_rebalance(self, symbol_weights: Dict[str, float]):
        weights_formatted = "\n".join([f"• <b>{sym}:</b> <code>{weight*100:.2f}%</code>" for sym, weight in symbol_weights.items()])
        message = (
            f"<b>⚖️ إعادة توازن أوزان المحفظة</b>\n\n"
            f"{weights_formatted}\n"
        )
        self.send_message(message)

    def notify_security_alert(self, filepath: str, issue_details: str):
        message = (
            f"<b>🚨 تنبيه أمني سيبراني عاجل (SecOps)</b>\n\n"
            f"<b>الملف:</b> <code>{filepath}</code>\n"
            f"<b>السبب:</b> {issue_details}\n"
        )
        self.send_message(message)
