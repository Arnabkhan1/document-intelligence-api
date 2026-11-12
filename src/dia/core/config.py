from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.
    Values are loaded from environment variables
    or the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "document-intelligence-api"
    app_version: str = "0.1.0"

    # Environment
    app_env: Literal["development", "testing", "production"] = "development"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.
    """
    return Settings()
