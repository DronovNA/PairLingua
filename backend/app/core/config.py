import pathlib
from functools import lru_cache
from typing import Optional, List, Union

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import field_validator

# Явная загрузка .env из корня проекта
env_path = pathlib.Path(".env")

load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Общие настройки
    APP_NAME: str = "PairLingua API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # База данных и редис
    DATABASE_URL: str
    REDIS_URL: str

    # JWT ключи
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS origins, валидатор для парсинга строки в список
    CORS_ORIGINS: Optional[Union[str, List[str]]] = "http://localhost:5173"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str], None]) -> List[str]:
        if not v:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            return [item.strip() for item in v.split(",") if item.strip()]
        raise ValueError("Invalid CORS_ORIGINS value")

    # Почта (опционально)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        # Явно указываем путь к .env (можно не указывать, если load_dotenv вызывается)
        env_file = str(env_path)
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
