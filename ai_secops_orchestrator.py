import logging
import re
import numpy as np

logger = logging.getLogger("SecOpsAI")

class CybersecurityAndMacroOrchestrator:
    """
    وكيل الفحص الأمني للأكواد والملفات + تحليل الأخبار الاقتصادية الكلية
    """
    def scan_code_security(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            api_key_pattern = r"['\"](?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{32,}['\"]"
            if re.search(api_key_pattern, content):
                logger.critical(f"[Security Risk]: تم اكتشاف مفتاح حساس صريح داخل {file_path}")
                return False
            return True
        except Exception as e:
            logger.error(f"خطأ أثناء التدقيق الأمني: {e}")
            return True

    def parse_macro_economic_news(self, text_content: str) -> float:
        hawkish_words = ["inflation", "rate hike", "tightening", "recession", "hawkish"]
        dovish_words = ["rate cut", "easing", "growth", "stimulus", "dovish"]
        
        score = 0.0
        words = text_content.lower().split()
        for w in words:
            if w in hawkish_words:
                score -= 0.15
            elif w in dovish_words:
                score += 0.15
        return float(np.clip(score, -1.0, 1.0))
