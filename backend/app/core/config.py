"""Конфигурация приложения Arbitr AI."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # === Application ===
    APP_NAME: str = "Arbitr AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "dev"  # dev | stage | prod

    # === API ===
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # === Database ===
    DATABASE_URL: str = "postgresql+asyncpg://Arbitr AI:Arbitr AI@localhost:5432/Arbitr AI"
    DATABASE_ECHO: bool = False

    # === Redis ===
    REDIS_URL: str = "redis://localhost:6379/0"

    # === Celery ===
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # === MinIO (S3) ===
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "Arbitr AI"
    MINIO_SECURE: bool = False

    # === JWT Auth ===
    SECRET_KEY: str = "change-me-in-production-use-harness-secrets"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # === LLM ===
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    YANDEXGPT_API_KEY: str = ""
    YANDEXGPT_FOLDER_ID: str = ""

    # === Integration: ФНС ===
    FNS_API_KEY: str = ""
    FNS_API_URL: str = "https://api-fns.ru"

    # === Integration: Росреестр ===
    ROSREESTR_API_KEY: str = ""
    ROSREESTR_API_URL: str = ""

    # === Integration: ФССП ===
    FSSP_API_KEY: str = ""
    FSSP_API_URL: str = ""

    # === Integration: Почта России ===
    POST_API_TOKEN: str = ""
    POST_API_URL: str = "https://api.pochta.ru"

    # === Email (SMTP) ===
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

    # === КриптоПро (ЭЦП) ===
    CRYPTOPRO_LICENSE: str = ""

    # === Feature Flags (Harness) ===
    FF_ENABLE_ROSREESTR_API: bool = False
    FF_ENABLE_AI_ANALYSIS: bool = True
    FF_ENABLE_EMAIL_DELIVERY: bool = False
    FF_ENABLE_NOTARY_INTEGRATION: bool = False
    FF_ENABLE_RPA_GIBDD: bool = False


@lru_cache
def get_settings() -> Settings:
    """Синглтон настроек."""
    return Settings()
