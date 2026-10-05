import asyncio
import json
import websockets
import logging
from config import config

logger = logging.getLogger("CapitalWebSocket")

class CapitalWebSocketClient:
    """بث وحصاد الأسعار اللحظية عبر WebSocket لمنصة Capital.com"""
    def __init__(self, epics: list[str], price_callback):
        self.epics = epics
        self.price_callback = price_callback
        self.is_running = False

    async def connect_and_listen(self):
        self.is_running = True
        headers = {
            "X-CAP-API-KEY": config.CAPITAL_API_KEY,
        }

        while self.is_running:
            try:
                async with websockets.connect(config.CAPITAL_WS_URL, extra_headers=headers) as ws:
                    logger.info("[WebSocket]: تم الاتصال بنجاح بخادم البث المباشر.")
                    
                    # إرسال طلب الاشتراك في الأسعار
                    subscribe_payload = {
                        "destination": "marketData.subscribe",
                        "payload": {"epics": self.epics}
                    }
                    await ws.send(json.dumps(subscribe_payload))

                    while self.is_running:
                        message = await ws.recv()
                        data = json.loads(message)
                        if "bid" in data and "offer" in data:
                            epic = data.get("epic")
                            bid = float(data.get("bid"))
                            offer = float(data.get("offer"))
                            await self.price_callback(epic, bid, offer)
            except Exception as e:
                logger.error(f"[WebSocket Error]: انقطع الاتصال: {e}. أعادة الاتصال خلال 5 ثوانٍ...")
                await asyncio.sleep(5)

    def stop(self):
        self.is_running = False
