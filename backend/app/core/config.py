from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Meridyen API"
    app_version: str = "0.1.0"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://meridyen:meridyen@localhost:5432/meridyen"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()