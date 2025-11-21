"""Configuration settings for the Kimi Chat History API."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server settings
    host: str = "127.0.0.1"
    port: int = 8001

    # CORS settings
    cors_origins: List[str] = ["http://localhost:8001", "http://localhost:8081", "null", "file://"]

    # Kimi data paths
    kimi_base_dir: Path = Path.home() / ".kimi"
    metadata_file: Path = kimi_base_dir / "kimi.json"
    sessions_dir: Path = kimi_base_dir / "sessions"
    user_history_dir: Path = kimi_base_dir / "user-history"

    # Caching
    cache_ttl: int = 300  # 5 minutes
    auto_refresh_interval: int = 300  # 5 minutes

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Truncation
    max_chat_name_length: int = 50
    max_message_preview: int = 100
    max_detail_messages: int = 1000

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
