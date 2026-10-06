import asyncio
import numpy as np
import pandas as pd
import logging

from config import config
from async_event_bus import AsyncEventBus, Event
from high_performance_engine import MicrostructureQuantEngine
from dynamic_kelly_garch import DynamicKellyGarchRiskEngine
from vector_macro_rag import VectorMacroSentimentAgent
from rl_execution_agent import PPOExecutionAgent
from telegram_notifier import TelegramNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("UltraInstitutionalCore")

class UltraInstitutionalSystem:
    """
    المحرك التنفيذي النهائي المطور بأعلى تقنيات HFT و Deep Learning
    """
    def __init__(self):
        logger.info("إطلاق النظام المطور بأساليب التداول الكمي عالي السرعة (HFT)...")
        self.bus = AsyncEventBus()
        self.high_perf = MicrostructureQuantEngine()
        self.risk_kelly = DynamicKellyGarchRiskEngine()
        self.macro_rag = VectorMacroSentimentAgent()
        self.rl_agent = PPOExecutionAgent()
        self.notifier = TelegramNotifier(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)

        self.bus.subscribe("MICROSTRUCTURE_TICK", self.process_microstructure_tick)

    async def process_microstructure_tick(self, data: dict):
        symbol = data["symbol"]
        prices = data["prices"]
        bid_prices = data["bid_prices"]
        bid_vols = data["bid_vols"]
        ask_prices = data["ask_prices"]
        ask_vols = data["ask_vols"]
        news = data.get("news", "")

        # 1. حساب عدم توازن تدفق الأوامر OFI ومؤشرات Polars فائقة السرعة
        ofi_val = self.high_perf.calculate_ofi(bid_prices, bid_vols, ask_prices, ask_vols)
        polars_metrics = self.high_perf.fast_polars_indicators(prices)

        # 2. تحليل الأخبار عبر محرك التضمين المتجهي Vector RAG
        macro_res = self.macro_rag.analyze_news_vector(news)
        macro_score = macro_res["macro_sentiment_score"]

        # 3. بناء متجه الحالة وتمريره لشبكة RL للتعلم التعزيزي
        returns_arr = np.diff(prices) / prices[:-1]
        state_vec = np.array([ofi_val, polars_metrics["returns"], polars_metrics["volatility"], macro_score, 0.5])
        rl_action = self.rl_agent.get_action(state_vec)

        # 4. إدارة المخاطر وتحديد حجم الصفقة بـ Dynamic Kelly + GARCH
        allocated_capital = self.risk_kelly.calculate_fractional_kelly_position(
            win_rate=0.62,
            win_loss_ratio=1.8,
            capital=100000.0,
            current_returns=returns_arr
        )

        # 5. واتخاذ القرار والتنفيذ
        if rl_action in [1, 2] and allocated_capital > 0:
            action_str = "BUY" if rl_action == 1 else "SELL"
            logger.info(f"🔥 إشارة HFT معتمدة: {action_str} على {symbol} | التخصيص: ${allocated_capital:.2f} | OFI: {ofi_val}")
            
            self.notifier.notify_trade_signal(
                symbol=symbol,
                action=action_str,
                price=prices[-1],
                rsi=55.0,
                trend="HFT Level 2 Order Flow",
                strategy=f"RL-PPO + Dynamic Kelly (${allocated_capital:.0f})"
            )

    async def start_simulated_stream(self):
        """
        محاكاة ضخ بيانات الميكروثانية والعمق L2
        """
        prices = [150.0, 150.05, 150.10, 150.08, 150.15]
        bid_prices = np.array([150.00, 150.05])
        bid_vols = np.array([1200, 1500])
        ask_prices = np.array([150.10, 150.15])
        ask_vols = np.array([800, 600])

        tick_data = {
            "symbol": "NVDA",
            "prices": prices,
            "bid_prices": bid_prices,
            "bid_vols": bid_vols,
            "ask_prices": ask_prices,
            "ask_vols": ask_vols,
            "news": "Federal Reserve signals potential rate cut as inflation drops."
        }

        await self.bus.publish(Event("MICROSTRUCTURE_TICK", tick_data))

if __name__ == "__main__":
    system = UltraInstitutionalSystem()
    asyncio.run(system.start_simulated_stream())
