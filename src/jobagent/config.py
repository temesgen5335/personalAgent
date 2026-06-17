"""Central settings, loaded from environment / .env via pydantic-settings.

Secrets live only in .env (gitignored) or the process environment — never in code.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM (OpenRouter)
    openrouter_api_key: str = Field("", alias="OPENROUTER_API_KEY")
    llm_model: str = Field("anthropic/claude-opus-4-8", alias="JOBAGENT_LLM_MODEL")
    embed_model: str = Field("openai/text-embedding-3-small", alias="JOBAGENT_EMBED_MODEL")

    # Telegram — channel reader (Telethon)
    telegram_api_id: int | None = Field(None, alias="TELEGRAM_API_ID")
    telegram_api_hash: str = Field("", alias="TELEGRAM_API_HASH")
    telegram_phone: str = Field("", alias="TELEGRAM_PHONE")
    # Telegram — bot you talk to (Bot API)
    telegram_bot_token: str = Field("", alias="TELEGRAM_BOT_TOKEN")
    telegram_owner_id: int | None = Field(None, alias="TELEGRAM_OWNER_ID")

    # Aggregator (Indeed/LinkedIn/Glassdoor/JobRight)
    serpapi_key: str = Field("", alias="SERPAPI_KEY")
    apify_token: str = Field("", alias="APIFY_TOKEN")

    # Store
    db_path: str = Field("data/jobagent.db", alias="JOBAGENT_DB_PATH")

    # Email (Tier 1 apply)
    smtp_host: str = Field("", alias="SMTP_HOST")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_user: str = Field("", alias="SMTP_USER")
    smtp_password: str = Field("", alias="SMTP_PASSWORD")
    apply_from_email: str = Field("", alias="APPLY_FROM_EMAIL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
