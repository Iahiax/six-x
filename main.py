import asyncio
import logging
import os
import sys
import threading
from typing import Dict

import numpy as np
import pandas as pd

from ai_secops_orchestrator import CybersecurityAndMacroOrchestrator
from async_event_bus import AsyncEventBus, Event
from broker_client import CapitalComClient
from config import config
from deep_alpha_ensemble import DeepAlphaEnsemble
from institutional_execution import InstitutionalExecutionEngine
from llm_agent_consensus import MultiAgentConsensusEngine
from market_universe import CapitalMarketUniverse
from massive_indicators import MassiveQuantIndicators
from risk_and_execution import RiskAndExecutionEngine
from state_persistence import SystemStateManager
from tail_risk_guard import TailRiskGuard
from telegram_control_bot import TelegramControlBot
from telegram_notifier import TelegramNotifier

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("InstitutionalCore")


class GlobalInstitutionalSystem:
    """النظام المؤسسي الرئيسي، جاهز للتشغيل الآمن في وضع DEMO افتراضيًا."""

    def __init__(self):
        self.trading_mode = config.TRADING_MODE
        logger.info("إطلاق البيئة المؤسسية الكاملة...")
        logger.info(f"وضع التداول الحالي: {self.trading_mode}")

        self.bus = AsyncEventBus()
        self.state_mgr = SystemStateManager()
        self.risk_engine = RiskAndExecutionEngine(self.state_mgr)
        self.broker = CapitalComClient()
        self.secops = CybersecurityAndMacroOrchestrator()
        self.notifier = TelegramNotifier(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)

        if not self._run_secops_audit():
            self.notifier.notify_security_alert(
                "main.py",
                "اكتشاف خلل في التدقيق الأمني السيبراني."
            )
            raise RuntimeError("فشل التدقيق الأمني. تم إيقاف النظام.")

        self.universe_scanner = CapitalMarketUniverse()
        self.consensus = MultiAgentConsensusEngine()
        self.alpha_engine = DeepAlphaEnsemble()
        self.risk_guard = TailRiskGuard()
        self.execution = InstitutionalExecutionEngine()

        if config.TELEGRAM_BOT_TOKEN:
            self.telegram_bot = TelegramControlBot(self.risk_engine, self.state_mgr, self.broker)
            self.telegram_bot.trading_mode = self.trading_mode
        else:
            self.telegram_bot = None
            logger.warning("لم يتم ضبط TELEGRAM_BOT_TOKEN، سيتم تشغيل النظام بدون بوت Telegram.")

        self.bus.subscribe("TICK_DATA", self.handle_tick_event)

    def _run_secops_audit(self) -> bool:
        for file_name in ["config.py", "main.py", "ai_secops_orchestrator.py"]:
            if not self.secops.scan_code_security(file_name):
                return False
        return True

    async def handle_tick_event(self, data: Dict):
        symbol = data["symbol"]
        df = data["dataframe"]
        returns_history = data["returns_history"]

        features = self.alpha_engine.extract_features(df)
        alpha_signal = self.alpha_engine.predict_alpha_signal(features)

        df["RSI"] = MassiveQuantIndicators.rsi(df["close"])
        kalman_prices = MassiveQuantIndicators.kalman_filter_smooth(df["close"].to_numpy())
        last_rsi = float(df["RSI"].iloc[-1])

        risk_score = self.risk_guard.evaluate_risk_clearance(returns_history, current_drawdown=0.01)

        decision = self.consensus.evaluate_trade_proposal(
            technical_signal=float(alpha_signal),
            macro_sentiment=0.35,
            risk_score=float(risk_score),
            secops_status=True,
        )

        if decision["approved"]:
            action = "BUY" if alpha_signal > 0.5 else "SELL"
            logger.info(f"تم اعتماد أمر {action} لـ {symbol} عبر محرك التوافق.")

            self.notifier.notify_trade_signal(
                symbol=symbol,
                action=action,
                price=float(df["close"].iloc[-1]),
                rsi=last_rsi,
                trend="Kalman Filtered Trend",
                strategy="Multi-Agent Deep Alpha Consensus",
            )

            await self.execution.execute_twap_order(
                symbol=symbol,
                total_quantity=50.0,
                side=action,
            )

    async def publish_demo_tick(self):
        dates = pd.date_range(end=pd.Timestamp.now(), periods=120, freq="1min")
        prices = 180 + np.cumsum(np.random.randn(len(dates)))

        df_mock = pd.DataFrame(
            {
                "open": prices,
                "high": prices + 0.5,
                "low": prices - 0.5,
                "close": prices,
                "volume": 20000,
            },
            index=dates,
        )
        returns_mock = pd.Series(np.random.randn(500) / 100)

        tick_event = Event(
            "TICK_DATA",
            {
                "symbol": "AAPL",
                "dataframe": df_mock,
                "returns_history": returns_mock,
            },
        )
        await self.bus.publish(tick_event)

    async def run(self):
        logger.info("بدء فحص قاعدة بيانات السوق...")
        self.universe_scanner.scan_full_universe()

        if self.telegram_bot is not None:
            logger.info("تشغيل بوت Telegram في الخلفية...")
            threading.Thread(target=self.telegram_bot.run_polling, daemon=True).start()

        for _ in range(3):
            await self.publish_demo_tick()
            await asyncio.sleep(5)

        logger.info("اكتمل التشغيل التجريبي الأولي في وضع %s", self.trading_mode)


if __name__ == "__main__":
    try:
        system = GlobalInstitutionalSystem()
        asyncio.run(system.run())
    except KeyboardInterrupt:
        logger.info("تم إيقاف النظام يدويًا.")
        sys.exit(0)
    except Exception as exc:
        logger.exception("حدث خطأ فادح أثناء تشغيل النظام: %s", exc)
        sys.exit(1)
