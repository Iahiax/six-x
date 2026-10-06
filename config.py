import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """التكوين المركزي للنظام."""

    # ==================== Capital.com API ====================
    CAPITAL_API_KEY: str = os.getenv("CAPITAL_API_KEY", "")
    CAPITAL_IDENTIFIER: str = os.getenv("CAPITAL_IDENTIFIER", "")
    CAPITAL_PASSWORD: str = os.getenv("CAPITAL_PASSWORD", "")
    CAPITAL_API_URL: str = os.getenv(
        "CAPITAL_API_URL",
        "https://demo-api-capital.backend-capital.com/api/v1",
    )
    CAPITAL_WS_URL: str = os.getenv(
        "CAPITAL_WS_URL",
        "wss://demo-api-streaming.backend-capital.com/connect",
    )
    CAPITAL_MODE: str = os.getenv("CAPITAL_MODE", "DEMO").upper()

    # ==================== Telegram ====================
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # ==================== SSH / Tor ====================
    SSH_HOSTNAME: str = os.getenv("SSH_HOSTNAME", "segfault.net")
    SSH_PORT: int = int(os.getenv("SSH_PORT", "22"))
    SSH_USERNAME: str = os.getenv("SSH_USERNAME", "root")
    SSH_KEY_PATH: str = os.getenv("SSH_KEY_PATH", "/root/.ssh/id_rsa")

    TOR_SOCKS_HOST: str = os.getenv("TOR_SOCKS_HOST", "127.0.0.1")
    TOR_SOCKS_PORT: int = int(os.getenv("TOR_SOCKS_PORT", "9050"))

    # ==================== Risk Controls ====================
    MAX_DAILY_DRAWDOWN_PCT: float = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", "0.05"))
    MAX_POSITION_SIZE_PCT: float = float(os.getenv("MAX_POSITION_SIZE_PCT", "0.05"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))
    MAX_SLIPPAGE_POINTS: float = float(os.getenv("MAX_SLIPPAGE_POINTS", "0.5"))

    # ==================== Consensus & Portfolio ====================
    CONSENSUS_THRESHOLD: float = float(os.getenv("CONSENSUS_THRESHOLD", "0.65"))
    DEFAULT_CAPITAL: float = float(os.getenv("DEFAULT_CAPITAL", "100000.0"))
    MAX_LEVERAGE: float = float(os.getenv("MAX_LEVERAGE", "2.0"))
    MAX_ASSET_WEIGHT: float = float(os.getenv("MAX_ASSET_WEIGHT", "0.35"))
    VPIN_THRESHOLD: float = float(os.getenv("VPIN_THRESHOLD", "0.50"))
    VPIN_WINDOW: int = int(os.getenv("VPIN_WINDOW", "50"))

    # ==================== Trading Mode ====================
    TRADING_MODE: str = os.getenv("TRADING_MODE", "DEMO").upper()
    DEMO_MODE: bool = TRADING_MODE == "DEMO"
    LIVE_MODE: bool = TRADING_MODE == "LIVE"

    # ==================== DB / Logs ====================
    QUESTDB_HOST: str = os.getenv("QUESTDB_HOST", "localhost")
    QUESTDB_PORT: int = int(os.getenv("QUESTDB_PORT", "9009"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/trading_system.log")


config = Config()
