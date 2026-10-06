import asyncio
import json
import websockets
import logging
from typing import Callable, Optional

logger = logging.getLogger("WebSocketStream")

class CapitalWebSocketClient:
    """
    عميل بث البيانات اللحظية والأسعار مباشرة عبر WebSocket
    """
    def __init__(self, ws_url: str, api_key: str, cst_token: str, xst_token: str):
        self.ws_url = ws_url
        self.api_key = api_key
        self.cst_token = cst_token
        self.xst_token = xst_token
        self.is_running = False
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

    async def connect_and_stream(self, epic_list: list, callback: Callable):
        self.is_running = True
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst_token,
            "X-SECURITY-TOKEN": self.xst_token
        }

        while self.is_running:
            try:
                logger.info("جاري الاتصال بـ WebSocket الخاص بالسوق...")
                async with websockets.connect(self.ws_url, extra_headers=headers) as ws:
                    self._ws = ws
                    logger.info("تم الاتصال بنجاح. إرسال طلب الاشتراكات للأصول...")
                    
                    subscribe_payload = {
                        "destination": "marketData.subscribe",
                        "correlationId": "1",
                        "cst": self.cst_token,
                        "securityToken": self.xst_token,
                        "payload": {"epics": epic_list}
                    }
                    await ws.send(json.dumps(subscribe_payload))

                    while self.is_running:
                        message = await ws.recv()
                        data = json.loads(message)
                        await callback(data)

            except websockets.ConnectionClosed:
                logger.warning("انقطع الاتصال بـ WebSocket. إعادة المحاولة خلال 3 ثوانٍ...")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"خطأ في تدفق البيانات الحية: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self.is_running = False
