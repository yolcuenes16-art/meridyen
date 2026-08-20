import secrets
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "Meridyen API"
    app_version: str = "0.2.0"
    debug: bool = True
    database_url: str = f"sqlite+aiosqlite:///{_BACKEND_DIR / 'meridyen.db'}"
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 60 * 24 * 30  # 30 days

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
