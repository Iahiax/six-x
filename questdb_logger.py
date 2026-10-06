import logging
from questdb.ingress import Sender, IngressError, TimestampNanos

logger = logging.getLogger("QuestDBLogger")

class QuestDBIngestionEngine:
    """
    محرك تسجيل السلاسل الزمنية عالي الكفاءة عبر QuestDB ILP
    """
    def __init__(self, host: str = "questdb", port: int = 9009):
        self.host = host
        self.port = port

    def log_tick(self, symbol: str, price: float, bid: float, ask: float, ofi: float, vol: float):
        """
        تسجيل بيانات التك والتوازن الميكروي في جدول market_ticks
        """
        try:
            with Sender.from_conf(f"tcp::host={self.host};port={self.port};") as sender:
                sender.row(
                    'market_ticks',
                    symbols={'symbol': symbol},
                    columns={
                        'price': float(price),
                        'bid': float(bid),
                        'ask': float(ask),
                        'ofi': float(ofi),
                        'volatility': float(vol)
                    },
                    at=TimestampNanos.now()
                )
                sender.flush()
        except IngressError as e:
            logger.error(f"خطأ أثناء كتابة التك إلى QuestDB: {e}")

    def log_execution(self, symbol: str, action: str, price: float, allocated_capital: float, latency_ms: float):
        """
        تسجيل قرارات وأحداث التنفيذ في جدول execution_logs
        """
        try:
            with Sender.from_conf(f"tcp::host={self.host};port={self.port};") as sender:
                sender.row(
                    'execution_logs',
                    symbols={'symbol': symbol, 'action': action},
                    columns={
                        'executed_price': float(price),
                        'capital': float(allocated_capital),
                        'latency_ms': float(latency_ms)
                    },
                    at=TimestampNanos.now()
                )
                sender.flush()
        except IngressError as e:
            logger.error(f"خطأ أثناء تسجيل التنفيذ في QuestDB: {e}")
