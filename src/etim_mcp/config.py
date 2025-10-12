"""Configuration management for ETIM MCP Server"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ETIM API Configuration
    etim_client_id: str
    etim_client_secret: str
    etim_auth_url: str = "https://etimauth.etim-international.com"
    etim_api_url: str = "https://etimapi.etim-international.com"
    etim_default_language: str = "EN"

    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""

    # Cache TTL Configuration (in seconds)
    cache_ttl: int = 3600  # 1 hour
    cache_class_ttl: int = 86400  # 24 hours
    cache_languages_ttl: int = 604800  # 7 days

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
