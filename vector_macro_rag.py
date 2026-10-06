import numpy as np
import logging
from typing import List, Dict

logger = logging.getLogger("VectorMacroRAG")

class VectorMacroSentimentAgent:
    """
    وكيل RAG المتجهي لاستخراج سياق الأخبار والسياسات النقدية باستخدام التشابه الاتجاهي
    """
    def __init__(self):
        # قاعدة معرفية مصغرة لمتجهات مفاهيم التضخم والفائدة
        self.knowledge_vectors = {
            "hawkish_inflation": np.array([0.8, 0.9, -0.4, 0.7]),
            "dovish_cut": np.array([-0.7, -0.8, 0.8, -0.6]),
            "neutral_stability": np.array([0.0, 0.1, 0.1, 0.0])
        }

    def _pseudo_embed_text(self, text: str) -> np.ndarray:
        """
        محاكاة خوارزمية التضمين النصي (Embeddings Vector) تحول النص لسلسلة أرقام اتجاهية
        """
        text_lower = text.lower()
        v1 = 0.8 if "rate hike" in text_lower or "inflation" in text_lower else -0.5
        v2 = 0.7 if "tightening" in text_lower or "hawkish" in text_lower else -0.4
        v3 = 0.8 if "rate cut" in text_lower or "easing" in text_lower else -0.3
        v4 = 0.6 if "gdp" in text_lower or "growth" in text_lower else 0.0
        
        vec = np.array([v1, v2, v3, v4])
        norm = np.linalg.norm(vec)
        return vec / norm if norm != 0 else vec

    def analyze_news_vector(self, news_text: str) -> Dict[str, float]:
        """
        قياس المسافة جيب التمام (Cosine Similarity) مع المتجهات المرجعية
        """
        query_vec = self._pseudo_embed_text(news_text)
        scores = {}

        for key, ref_vec in self.knowledge_vectors.items():
            cosine_sim = np.dot(query_vec, ref_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(ref_vec) + 1e-9)
            scores[key] = float(cosine_sim)

        macro_score = scores["dovish_cut"] - scores["hawkish_inflation"]
        logger.info(f"نتيجة التحليل المتجهي للخبر: {macro_score:.3f}")
        
        return {
            "macro_sentiment_score": float(np.clip(macro_score, -1.0, 1.0)),
            "similarity_scores": scores
        }
