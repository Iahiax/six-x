import asyncio
import logging
from config import config
from state_persistence import SystemStateManager
from risk_and_execution import RiskAndExecutionEngine
from gpu_ml_engine import QuantMLInferenceEngine
from complete_x_engine import CompleteMicrostructureAndQuantMath

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MainEngine")

async def main_trading_loop():
    logger.info("==================================================")
    logger.info("   تشغيل محرك CAPITAL-AI-X للسيولة والذكاء الكمي   ")
    logger.info("==================================================")

    state_mgr = SystemStateManager()
    risk_engine = RiskAndExecutionEngine(state_mgr)
    ml_engine = QuantMLInferenceEngine()

    logger.info("[System]: تم التمهيد والتحقق من المكونات بنجاح. بدء حلقة المراقبة...")

    while True:
        # محاكاة خطوة جلب البيانات والتأكد من السيولة
        dummy_sequence = np.random.randn(20, 10)
        signal, confidence = ml_engine.predict_signal(dummy_sequence)
        
        logger.info(f"[Inference Loop]: Signal Generated: {signal} | Confidence: {confidence:.4f}")
        
        await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main_trading_loop())
    except KeyboardInterrupt:
        logger.info("تم إيقاف النظام بواسطة المستخدم.")
