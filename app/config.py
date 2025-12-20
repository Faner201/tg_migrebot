from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = "CHANGEME"
    postgres_dsn: str = "postgresql+asyncpg://migrebot:migrebot@postgres:5432/migrebot"
    redis_url: str = "redis://redis:6379/0"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()



