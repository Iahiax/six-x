import asyncio
import pandas as pd
import numpy as np
import logging
import sys
from typing import Dict

from config import config
from async_event_bus import AsyncEventBus, Event
from market_universe import CapitalMarketUniverse
from massive_indicators import MassiveQuantIndicators
from llm_agent_consensus import MultiAgentConsensusEngine
from deep_alpha_ensemble import DeepAlphaEnsemble
from tail_risk_guard import TailRiskGuard
from institutional_execution import InstitutionalExecutionEngine
from ai_secops_orchestrator import CybersecurityAndMacroOrchestrator
from telegram_notifier import TelegramNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("InstitutionalCore")

class GlobalInstitutionalSystem:
    """
    المحرك النهائي والتنفيذي الرئيسي لجميع مكونات البيئة المتقدمة
    """
    def __init__(self):
        logger.info("إطلاق البيئة المؤسسية الكاملة...")
        self.bus = AsyncEventBus()
        self.secops = CybersecurityAndMacroOrchestrator()
        self.notifier = TelegramNotifier(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
        
        # فحص الأمان عند الانطلاق
        if not self._run_secops_audit():
            self.notifier.notify_security_alert("main.py", "اكتشاف خلل في التدقيق الأمني السيبراني.")
            sys.exit(1)

        self.universe_scanner = CapitalMarketUniverse()
        self.consensus = MultiAgentConsensusEngine()
        self.alpha_engine = DeepAlphaEnsemble()
        self.risk_guard = TailRiskGuard()
        self.execution = InstitutionalExecutionEngine()

        # ربط الأحداث
        self.bus.subscribe("TICK_DATA", self.handle_tick_event)

    def _run_secops_audit(self) -> bool:
        for f in ["config.py", "main.py", "ai_secops_orchestrator.py"]:
            if not self.secops.scan_code_security(f):
                return False
        return True

    async def handle_tick_event(self, data: Dict):
        symbol = data['symbol']
        df = data['dataframe']
        returns_history = data['returns_history']

        # 1. استخراج معالم التعلم الآلي وإشارة الألفا
        features = self.alpha_engine.extract_features(df)
        alpha_signal = self.alpha_engine.predict_alpha_signal(features)

        # 2. قياس مؤشر RSI والاتجاه بمرشح كالمان
        df['RSI'] = MassiveQuantIndicators.rsi(df['close'])
        kalman_prices = MassiveQuantIndicators.kalman_filter_smooth(df['close'].to_numpy())
        last_rsi = df['RSI'].iloc[-1]

        # 3. حساب درجة المخاطرة
        risk_score = self.risk_guard.evaluate_risk_clearance(returns_history, current_drawdown=0.01)

        # 4. تقييم توافق الوكلاء (Consensus)
        decision = self.consensus.evaluate_trade_proposal(
            technical_signal=alpha_signal,
            macro_sentiment=0.35,
            risk_score=risk_score,
            secops_status=True
        )

        # 5. التنبيه والتنفيذ
        if decision['approved']:
            action = "BUY" if alpha_signal > 0.5 else "SELL"
            logger.info(f"تم اعتماد أمر {action} لـ {symbol} عبر محرك التوافق.")
            
            self.notifier.notify_trade_signal(
                symbol=symbol,
                action=action,
                price=df['close'].iloc[-1],
                rsi=last_rsi,
                trend="Kalman Filtered Trend",
                strategy="Multi-Agent Deep Alpha Consensus"
            )

            await self.execution.execute_twap_order(symbol, total_quantity=50.0, side=action)

    async def run(self):
        logger.info("مسح قاعدة بيانات Capital.com...")
        self.universe_scanner.scan_full_universe()

        # محاكاة تدفق أسبوعي حي
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1min')
        prices = 180 + np.cumsum(np.random.randn(100))
        df_mock = pd.DataFrame({
            'open': prices, 'high': prices + 0.5, 'low': prices - 0.5, 'close': prices, 'volume': 20000
        }, index=dates)
        returns_mock = pd.Series(np.random.randn(500) / 100)

        tick_event = Event("TICK_DATA", {
            "symbol": "AAPL",
            "dataframe": df_mock,
            "returns_history": returns_mock
        })

        await self.bus.publish(tick_event)

if __name__ == "__main__":
    system = GlobalInstitutionalSystem()
    asyncio.run(system.run())
