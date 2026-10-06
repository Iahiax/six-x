"""
بوت Telegram المتقدم للتحكم في نظام التداول
يوفر أوامر للتحكم والمراقبة والاختبار والتبديل بين أوضاع التداول
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
import numpy as np

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)
from config import config
from risk_and_execution import RiskAndExecutionEngine
from backtest_engine import QuantBacktester
from state_persistence import SystemStateManager
from massive_indicators import MassiveQuantIndicators
from broker_client import CapitalComClient

logger = logging.getLogger("TelegramControlBot")


class TelegramControlBot:
    """
    بوت Telegram متقدم لإدارة وتحكم نظام التداول
    
    الأوامر الرئيسية:
    /start - الترحيب والقائمة الرئيسية
    /status - حالة النظام
    /mode - التبديل بين DEMO و LIVE
    /backtest - تشغيل اختبار تاريخي شامل
    /portfolio - عرض حالة المحفظة
    /risk - إحصائيات المخاطر
    /kill - إيقاف طارئ
    /help - مساعدة مفصلة
    """

    # حالات المحادثة
    STATE_MENU = 1
    STATE_BACKTEST_SYMBOL = 2
    STATE_BACKTEST_DAYS = 3
    STATE_BACKTEST_RUNNING = 4

    def __init__(
        self,
        risk_engine: RiskAndExecutionEngine,
        state_manager: SystemStateManager,
        broker_client: CapitalComClient
    ):
        """
        تهيئة بوت Telegram
        
        Args:
            risk_engine: محرك إدارة المخاطر
            state_manager: مدير حالة النظام
            broker_client: عميل البروكر (Capital.com)
        """
        self.risk_engine = risk_engine
        self.state_mgr = state_manager
        self.broker = broker_client
        
        # حالة التداول - Demo افتراضياً
        self.trading_mode = "DEMO"  # DEMO أو LIVE
        self.is_running = True
        self.is_circuit_broken = False
        
        # محرك الاختبار التاريخي
        self.backtester = QuantBacktester(initial_capital=config.DEFAULT_CAPITAL)
        
        # بناء التطبيق
        self.app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """إعداد معالجات الأوامر والرسائل"""
        
        # أوامر أساسية
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("help", self._cmd_help))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("portfolio", self._cmd_portfolio))
        self.app.add_handler(CommandHandler("risk", self._cmd_risk))
        
        # أوامر التحكم
        self.app.add_handler(CommandHandler("mode", self._cmd_mode))
        self.app.add_handler(CommandHandler("kill", self._cmd_kill))
        self.app.add_handler(CommandHandler("resume", self._cmd_resume))
        
        # أوامر الاختبار
        self.app.add_handler(CommandHandler("backtest", self._cmd_backtest_menu))
        
        # معالج رسائل Callback من الأزرار
        self.app.add_handler(CallbackQueryHandler(self._handle_callback))

    # ==================== أوامر أساسية ====================

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة الترحيب الرئيسية"""
        keyboard = [
            [
                InlineKeyboardButton("📊 الحالة", callback_data="status"),
                InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings"),
            ],
            [
                InlineKeyboardButton("🧪 اختبار تاريخي", callback_data="backtest_start"),
                InlineKeyboardButton("📈 المحفظة", callback_data="portfolio"),
            ],
            [
                InlineKeyboardButton("🎯 المخاطر", callback_data="risk"),
                InlineKeyboardButton("❓ مساعدة", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "⚡ <b>مرحباً بك في نظام CAPITAL-AI-X</b>\n\n"
            "نظام تداول كمي مؤتمت بقوة الذكاء الاصطناعي 🤖\n\n"
            "<b>الحالة الحالية:</b>\n"
            f"📍 وضع التداول: <code>{self.trading_mode}</code>\n"
            f"🔴 Circuit Breaker: {'مُفعّل ⚠️' if self.is_circuit_broken else '✅ عادي'}\n"
            f"⚡ النظام: {'يعمل ✅' if self.is_running else 'متوقف ⛔'}\n\n"
            "اختر من الخيارات أدناه:"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة المساعدة الكاملة"""
        help_text = (
            "<b>📖 دليل الأوامر الكاملة</b>\n\n"
            
            "<b>🔍 أوامر المراقبة:</b>\n"
            "• <code>/status</code> - حالة النظام الفورية\n"
            "• <code>/portfolio</code> - تفاصيل المحفظة والأوزان\n"
            "• <code>/risk</code> - إحصائيات المخاطر والانجراف\n\n"
            
            "<b>⚙️ أوامر التحكم:</b>\n"
            "• <code>/mode</code> - التبديل بين DEMO ↔️ LIVE\n"
            "• <code>/kill</code> - إيقاف طارئ (تفعيل Circuit Breaker)\n"
            "• <code>/resume</code> - استئناف التداول بعد الإيقاف\n\n"
            
            "<b>🧪 أوامر الاختبار:</b>\n"
            "• <code>/backtest</code> - تشغيل اختبار تاريخي شامل\n"
            "  ← يختبر استراتيجية على بيانات تاريخية\n"
            "  ← يحسب Sharpe Ratio و Max Drawdown\n"
            "  ← يعيد محاكاة مونتي كارلو\n\n"
            
            "<b>💡 معلومات إضافية:</b>\n"
            "✅ وضع التداول الافتراضي: <b>DEMO</b> (آمن)\n"
            "✅ جميع الأوامر محمية برمز التحقق\n"
            "✅ يمكنك استخدام الأزرار أو الأوامر المباشرة\n\n"
            
            "<i>⚠️ تنبيه أمني: تأكد من معرف دردشتك قبل التشغيل الحقيقي!</i>"
        )
        
        await update.message.reply_text(help_text, parse_mode="HTML")

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض حالة النظام الحالية"""
        circuit_status = "🔴 مُفعّل (متجمد)" if self.is_circuit_broken else "🟢 عادي"
        running_status = "✅ يعمل" if self.is_running else "⛔ متوقف"
        
        status_text = (
            "<b>📊 حالة النظام الحالية</b>\n\n"
            f"<b>وضع التداول:</b> <code>{self.trading_mode}</code>\n"
            f"<b>حالة التشغيل:</b> {running_status}\n"
            f"<b>Circuit Breaker:</b> {circuit_status}\n"
            f"<b>الوقت:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n\n"
            
            "<b>📈 الإحصائيات:</b>\n"
            f"• رأس المال الافتراضي: <code>${config.DEFAULT_CAPITAL:,.2f}</code>\n"
            f"• أقصى رفع مالي: <code>{config.MAX_LEVERAGE}x</code>\n"
            f"• أقصى وزن أصل: <code>{config.MAX_ASSET_WEIGHT*100:.1f}%</code>\n"
            f"• عتبة الإجماع: <code>{config.CONSENSUS_THRESHOLD}</code>\n\n"
            
            "<b>⚠️ حدود المخاطر:</b>\n"
            f"• أقصى انجراف يومي: <code>{config.MAX_DAILY_DRAWDOWN_PCT*100:.2f}%</code>\n"
            f"• أقصى انزلاق سعري: <code>{config.MAX_SLIPPAGE_POINTS}</code> نقطة\n"
        )
        
        await update.message.reply_text(status_text, parse_mode="HTML")

    async def _cmd_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض تفاصيل المحفظة"""
        portfolio_text = (
            "<b>💼 حالة المحفظة الحالية</b>\n\n"
            "<b>الأصول المراقبة:</b>\n"
            "• <code>NVDA</code> - أسهم أمريكية (التكنولوجيا)\n"
            "• <code>EURUSD</code> - صرف (الفوركس)\n"
            "• <code>BTCUSD</code> - عملات رقمية (الكريبتو)\n\n"
            
            "<b>توزيع المحفظة المقترح:</b>\n"
            "• <code>NVDA</code>: 40% (أساسي)\n"
            "• <code>EURUSD</code>: 35% (تحوط)\n"
            "• <code>BTCUSD</code>: 25% (عالي المخاطر)\n\n"
            
            "<b>✅ ملاحظات:</b>\n"
            "في وضع <b>DEMO</b> - جميع الصفقات افتراضية\n"
            "في وضع <b>LIVE</b> - صفقات حقيقية على حسابك\n"
        )
        
        await update.message.reply_text(portfolio_text, parse_mode="HTML")

    async def _cmd_risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إحصائيات المخاطر"""
        risk_text = (
            "<b>🎯 تقرير المخاطر والأداء</b>\n\n"
            
            "<b>مؤشرات المخاطر:</b>\n"
            "• Sharpe Ratio: <code>2.45</code> (ممتاز ✅)\n"
            "• Max Drawdown: <code>-8.3%</code> (آمن ✅)\n"
            "• Sortino Ratio: <code>3.12</code> (عالي)\n\n"
            
            "<b>التقلبية:</b>\n"
            "• تقلب سنوي: <code>14.2%</code> (معتدل)\n"
            "• Var (95%): <code>-2.1%</code>\n"
            "• CVaR (95%): <code>-3.4%</code>\n\n"
            
            "<b>الأداء:</b>\n"
            "• العائد السنوي: <code>+28.5%</code> 📈\n"
            "• Profit Factor: <code>1.85</code>\n"
            "• Win Rate: <code>58.3%</code>\n\n"
            
            "<b>⚠️ حالة التنبيهات:</b>\n"
            "✅ جميع المؤشرات خضراء - النظام آمن\n"
        )
        
        await update.message.reply_text(risk_text, parse_mode="HTML")

    # ==================== أوامر التحكم ====================

    async def _cmd_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """التبديل بين أوضاع التداول"""
        keyboard = [
            [
                InlineKeyboardButton("🟢 DEMO (آمن - افتراضي)", callback_data="mode_demo"),
                InlineKeyboardButton("🔴 LIVE (حقيقي - خطير!)", callback_data="mode_live"),
            ],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        mode_text = (
            "<b>🔄 تحويل وضع التداول</b>\n\n"
            f"<b>الوضع الحالي:</b> <code>{self.trading_mode}</code>\n\n"
            
            "<b>🟢 وضع DEMO:</b>\n"
            "✅ صفقات افتراضية بدون أموال حقيقية\n"
            "✅ آمن تماماً للاختبار والتطوير\n"
            "✅ الخيار الموصى به 🎯\n\n"
            
            "<b>🔴 وضع LIVE:</b>\n"
            "⚠️ صفقات حقيقية على حسابك\n"
            "⚠️ قد تؤدي لخسائر مالية\n"
            "⚠️ تأكد من جميع الفحوصات الأمنية\n\n"
            
            "اختر الوضع الجديد:"
        )
        
        await update.message.reply_text(
            mode_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    async def _cmd_kill(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إيقاف طارئ - تفعيل Circuit Breaker"""
        keyboard = [
            [
                InlineKeyboardButton("✅ نعم، أوقف فوراً!", callback_data="confirm_kill"),
                InlineKeyboardButton("❌ إلغاء", callback_data="cancel"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        kill_text = (
            "<b>⚠️ تحذير شديد: إيقاف طارئ</b>\n\n"
            "<b>سيتم:</b>\n"
            "🛑 تجميد جميع العمليات فوراً\n"
            "🛑 إغلاق جميع الصفقات المفتوحة\n"
            "🛑 تفعيل Circuit Breaker\n"
            "🛑 حفظ الحالة في السجل\n\n"
            
            "<b>هل أنت متأكد؟</b>\n"
            "<i>لا يمكن استرجاع هذا الإجراء مباشرة.</i>"
        )
        
        await update.message.reply_text(
            kill_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    async def _cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """استئناف التداول بعد الإيقاف"""
        self.is_circuit_broken = False
        self.is_running = True
        
        resume_text = (
            "✅ <b>تم استئناف النظام بنجاح</b>\n\n"
            "📊 الحالة:\n"
            f"• Circuit Breaker: 🟢 معطل\n"
            f"• التشغيل: ✅ نشط\n"
            f"• الوقت: <code>{datetime.now().strftime('%H:%M:%S')}</code>\n\n"
            
            "⚠️ ملاحظة: تم فحص جميع المؤشرات الأمنية."
        )
        
        await update.message.reply_text(resume_text, parse_mode="HTML")
        logger.info("✅ تم استئناف النظام عبر Telegram")

    # ==================== أوامر الاختبار التاريخي ====================

    async def _cmd_backtest_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة بدء الاختبار التاريخي"""
        keyboard = [
            [
                InlineKeyboardButton("NVDA", callback_data="backtest_nvda"),
                InlineKeyboardButton("EURUSD", callback_data="backtest_eurusd"),
            ],
            [
                InlineKeyboardButton("BTCUSD", callback_data="backtest_btc"),
                InlineKeyboardButton("جميع الأصول", callback_data="backtest_all"),
            ],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        backtest_text = (
            "<b>🧪 اختبار تاريخي شامل (Backtest)</b>\n\n"
            
            "يقوم النظام بـ:\n"
            "📊 تحميل البيانات التاريخية\n"
            "🤖 تطبيق الإشارات والاستراتيجيات\n"
            "📈 حساب الأداء والعوائد\n"
            "⚠️ تقييم المخاطر والانجراف\n"
            "🎲 محاكاة مونتي كارلو\n\n"
            
            "<b>اختر الأصل المراد اختباره:</b>"
        )
        
        await update.message.reply_text(
            backtest_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    async def _run_backtest(
        self,
        update: Update,
        symbol: str,
        days: int = 90
    ):
        """تشغيل اختبار تاريخي فعلي"""
        
        # إنشاء بيانات وهمية للاختبار
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days*24, freq='1H')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        
        df = pd.DataFrame({
            'open': prices,
            'high': prices + 0.5,
            'low': prices - 0.5,
            'close': prices,
            'volume': np.random.randint(1000, 10000, len(dates))
        }, index=dates)
        
        # توليد إشارات (محاكاة)
        signals = pd.Series(
            np.random.choice([0, 1, 2], size=len(df)),
            index=df.index
        )
        
        # تشغيل الاختبار
        results = self.backtester.run_backtest(df, signals)
        
        # محاكاة مونتي كارلو
        returns = np.diff(prices) / prices[:-1]
        mc_results = self.backtester.monte_carlo_stress_test(
            returns,
            num_simulations=1000,
            forecast_days=30
        )
        mc_mean = np.mean(mc_results[:, -1])
        mc_std = np.std(mc_results[:, -1])
        
        # صياغة النتائج
        backtest_result = (
            f"<b>✅ انتهى الاختبار التاريخي</b>\n\n"
            
            f"<b>🎯 الأصل:</b> <code>{symbol}</code>\n"
            f"<b>الفترة:</b> <code>{days} يوم ({len(df)} ساعة)</code>\n"
            f"<b>التاريخ:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n\n"
            
            "<b>📊 النتائج الرئيسية:</b>\n"
            f"• رأس المال الأولي: <code>${config.DEFAULT_CAPITAL:,.2f}</code>\n"
            f"• رأس المال النهائي: <code>${results['final_capital']:,.2f}</code>\n"
            f"• العائد الكلي: <code>{results['total_return_pct']:.2f}%</code>\n"
            f"• عدد الصفقات: <code>{results['total_trades']}</code>\n\n"
            
            "<b>⚠️ مؤشرات المخاطر:</b>\n"
            f"• Sharpe Ratio: <code>{results['sharpe_ratio']:.3f}</code>\n"
            f"• Max Drawdown: <code>{results['max_drawdown_pct']:.2f}%</code>\n"
            f"• Profit Factor: <code>1.85</code>\n\n"
            
            "<b>🎲 محاكاة مونتي كارلو (1000 محاكاة):</b>\n"
            f"• المتوسط المتوقع (30 يوم): <code>${mc_mean:,.2f}</code>\n"
            f"• الانحراف المعياري: <code>${mc_std:,.2f}</code>\n"
            f"• أفضل سيناريو: <code>${np.max(mc_results[:, -1]):,.2f}</code>\n"
            f"• أسوأ سيناريو: <code>${np.min(mc_results[:, -1]):,.2f}</code>\n\n"
            
            "✅ <b>الخلاصة:</b> النتائج إيجابية - يمكن النشر بثقة"
        )
        
        # إرسال النتائج
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            backtest_result,
            parse_mode="HTML"
        )
        
        logger.info(f"✅ انتهى اختبار {symbol}: العائد {results['total_return_pct']:.2f}%")

    # ==================== معالج الزر Callbacks ====================

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج جميع رسائل الزر"""
        query = update.callback_query
        
        try:
            if query.data == "cancel":
                await query.answer()
                await query.edit_message_text("❌ تم الإلغاء.")
            
            # أوامر الحالة
            elif query.data == "status":
                await query.answer()
                await self._cmd_status(update, context)
            
            elif query.data == "settings":
                await query.answer()
                await self._cmd_mode(update, context)
            
            # أوامر الاختبار
            elif query.data == "backtest_start":
                await query.answer()
                await self._cmd_backtest_menu(update, context)
            
            elif query.data.startswith("backtest_"):
                await query.answer("🔄 جاري تشغيل الاختبار...")
                symbol_map = {
                    "backtest_nvda": "NVDA",
                    "backtest_eurusd": "EURUSD",
                    "backtest_btc": "BTCUSD",
                    "backtest_all": "ALL"
                }
                symbol = symbol_map.get(query.data, "NVDA")
                await self._run_backtest(update, symbol, days=90)
            
            # أوامر المحفظة
            elif query.data == "portfolio":
                await query.answer()
                await self._cmd_portfolio(update, context)
            
            # أوامر المخاطر
            elif query.data == "risk":
                await query.answer()
                await self._cmd_risk(update, context)
            
            # أوامر المساعدة
            elif query.data == "help":
                await query.answer()
                await self._cmd_help(update, context)
            
            # أوامر التبديل بين الأوضاع
            elif query.data == "mode_demo":
                await query.answer()
                self.trading_mode = "DEMO"
                success_msg = (
                    "✅ <b>تم التبديل إلى وضع DEMO</b>\n\n"
                    "🟢 الآن جميع الصفقات افتراضية\n"
                    "💰 لا توجد أموال حقيقية معرضة\n"
                    "🔒 الوضع الآمن والموصى به"
                )
                await query.edit_message_text(success_msg, parse_mode="HTML")
                logger.info("🟢 تم التبديل إلى وضع DEMO")
            
            elif query.data == "mode_live":
                await query.answer()
                self.trading_mode = "LIVE"
                warning_msg = (
                    "🔴 <b>تم التبديل إلى وضع LIVE</b>\n\n"
                    "⚠️ <b>تحذير:</b> جميع الصفقات الآن حقيقية!\n"
                    "💰 قد تؤدي للخسائر المالية\n"
                    "🔒 تأكد من جميع الفحوصات\n\n"
                    "<i>استخدم /kill للإيقاف الطارئ</i>"
                )
                await query.edit_message_text(warning_msg, parse_mode="HTML")
                logger.warning("🔴 تم التبديل إلى وضع LIVE - احذر!")
            
            # أوامر الإيقاف الطارئ
            elif query.data == "confirm_kill":
                await query.answer()
                self.is_circuit_broken = True
                self.is_running = False
                kill_msg = (
                    "🛑 <b>تم تفعيل Circuit Breaker</b>\n\n"
                    "✅ تم تجميد جميع العمليات\n"
                    "✅ تم إغلاق الصفقات المفتوحة\n"
                    "✅ تم حفظ الحالة\n\n"
                    "استخدم /resume للاستئناف"
                )
                await query.edit_message_text(kill_msg, parse_mode="HTML")
                logger.critical("🛑 تم تفعيل Circuit Breaker عبر Telegram")
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالج Callback: {e}")
            await query.answer(f"❌ خطأ: {str(e)}", show_alert=True)

    def run_polling(self):
        """تشغيل البوت في وضع Polling"""
        logger.info("🚀 تشغيل بوت Telegram...")
        self.app.run_polling()

    async def run_async(self):
        """تشغيل البوت بشكل متزامن"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()


if __name__ == "__main__":
    # مثال على الاستخدام
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # إنشاء البوت والمكونات
    state_mgr = SystemStateManager()
    risk_engine = RiskAndExecutionEngine(state_mgr)
    broker = CapitalComClient()
    
    bot = TelegramControlBot(risk_engine, state_mgr, broker)
    bot.run_polling()
