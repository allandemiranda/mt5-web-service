from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables (.env)."""

    # Web Service Settings
    APP_NAME: str = "MT5 Web Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # MetaTrader 5 Static Credentials & Parameters
    MT5_LOGIN: Optional[int] = None
    MT5_PASSWORD: Optional[str] = None
    MT5_SERVER: Optional[str] = None
    MT5_PATH: Optional[str] = None
    MT5_PORTABLE: bool = False
    MT5_TIMEOUT: int = 60000  # in milliseconds

    # Reconnection & Monitoring Settings
    MT5_HEARTBEAT_INTERVAL: float = 5.0  # seconds between terminal health checks
    MT5_RETRY_BASE_DELAY: float = 2.0  # initial reconnection delay in seconds
    MT5_RETRY_MAX_DELAY: float = 30.0  # maximum reconnection delay in seconds
    MT5_RETRY_BACKOFF_FACTOR: float = 1.5  # exponential backoff multiplier

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
