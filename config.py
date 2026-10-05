import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    # Capital.com API Credentials
    CAPITAL_API_KEY: str = os.getenv("CAPITAL_API_KEY", "")
    CAPITAL_IDENTIFIER: str = os.getenv("CAPITAL_IDENTIFIER", "")
    CAPITAL_PASSWORD: str = os.getenv("CAPITAL_PASSWORD", "")
    CAPITAL_API_URL: str = os.getenv("CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1")
    CAPITAL_WS_URL: str = os.getenv("CAPITAL_WS_URL", "wss://demo-api-streaming.backend-capital.com/connect")

    # Telegram Control & Alerts
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Segfault SSH VPS Settings
    SSH_HOSTNAME: str = os.getenv("SSH_HOSTNAME", "segfault.net")
    SSH_PORT: int = int(os.getenv("SSH_PORT", "22"))
    SSH_USERNAME: str = os.getenv("SSH_USERNAME", "root")
    SSH_KEY_PATH: str = os.getenv("SSH_KEY_PATH", "/root/.ssh/id_rsa")

    # Tor Network SOCKS5 Settings
    TOR_SOCKS_HOST: str = os.getenv("TOR_SOCKS_HOST", "127.0.0.1")
    TOR_SOCKS_PORT: int = int(os.getenv("TOR_SOCKS_PORT", "9050"))

    # Quant & Risk Controls
    MAX_DAILY_DRAWDOWN_PCT: float = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", "0.05"))
    MAX_POSITION_SIZE_PCT: float = float(os.getenv("MAX_POSITION_SIZE_PCT", "0.05"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))
    MAX_SLIPPAGE_POINTS: float = float(os.getenv("MAX_SLIPPAGE_POINTS", "0.5"))

config = Config()
