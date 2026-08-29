from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IC Research Copilot API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+asyncpg://ic_copilot:ic_copilot@localhost:5432/ic_copilot"
    )
    redis_url: str = "redis://localhost:6379/0"
    semantic_scholar_api_key: str | None = None
    crossref_mailto: str | None = None
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-5-mini"
    request_timeout_seconds: float = 12.0

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

