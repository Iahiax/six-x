import requests
import logging
from config import config

logger = logging.getLogger("TorScraper")

class TorDarkwebScraper:
    """جالب الأخبار والمشاعر مع دعم كامل لبروكسي Tor SOCKS5"""
    def __init__(self):
        self.proxies = {
            'http': f'socks5h://{config.TOR_SOCKS_HOST}:{config.TOR_SOCKS_PORT}',
            'https': f'socks5h://{config.TOR_SOCKS_HOST}:{config.TOR_SOCKS_PORT}'
        }

    def fetch_onion_sentiment(self, onion_url: str) -> str:
        """جلب وتحليل النصوص من الروابط المخفية (.onion) عبر شبكة Tor"""
        try:
            response = requests.get(onion_url, proxies=self.proxies, timeout=15)
            if response.status_code == 200:
                return response.text[:2000] # اقتطاع النص الأول
            return ""
        except Exception as e:
            logger.warning(f"[Tor Scraper Warning]: تعذر الوصول إلى {onion_url}: {e}")
            return ""
