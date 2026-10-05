import logging
from typing import Dict, Any
from config import config

logger = logging.getLogger("AgentConsensus")

class MultiAgentConsensusEngine:
    """
    محرك التصويت والحوكمة متعدد الوكلاء الذكي
    """
    def __init__(self):
        self.threshold_score = config.CONSENSUS_THRESHOLD

    def evaluate_trade_proposal(
        self,
        technical_signal: float,
        macro_sentiment: float,
        risk_score: float,
        secops_status: bool
    ) -> Dict[str, Any]:
        if not secops_status:
            logger.critical("رفض الصفقة: وكيل الأمن السيبراني رصد مخاطر!")
            return {"approved": False, "reason": "SecOps Veto", "final_score": 0.0}

        w_tech = 0.35
        w_macro = 0.25
        w_risk = 0.40

        normalized_macro = (macro_sentiment + 1.0) / 2.0
        final_score = (technical_signal * w_tech) + (normalized_macro * w_macro) + (risk_score * w_risk)
        approved = final_score >= self.threshold_score

        logger.info(f"نتيجة التصويت النهائية: {final_score:.2f} | القرار: {'موافقة' if approved else 'رفض'}")

        return {
            "approved": approved,
            "final_score": final_score,
            "agent_breakdown": {
                "technical": technical_signal,
                "macro": normalized_macro,
                "risk": risk_score,
                "secops": secops_status
            }
        }
