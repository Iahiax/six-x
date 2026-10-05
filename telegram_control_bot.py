import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import config
from risk_and_execution import RiskAndExecutionEngine

class TelegramControlBot:
    """بوت تليجرام ثنائي الاتجاه لاستقبال الأوامر إرسال التنبيهات"""
    def __init__(self, risk_engine: RiskAndExecutionEngine):
        self.risk_engine = risk_engine
        self.app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("kill", self._cmd_kill))

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚡ CAPITAL-AI-X Bot Ready.\n/status - فحص الحالة\n/kill - إيقاف طارئ")

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        cb_status = "🔴 ACTIVE (FROZEN)" if self.risk_engine.is_circuit_broken else "🟢 NORMAL"
        await update.message.reply_text(f"📊 **حالة النظام:**\nCircuit Breaker: {cb_status}")

    async def _cmd_kill(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.risk_engine.trigger_circuit_breaker("Manual Kill Command via Telegram")
        await update.message.reply_text("🚨 **تم تفعيل قاطع التيار وتجميد العمليات بنجاح.**")

    def run_polling(self):
        self.app.run_polling()
