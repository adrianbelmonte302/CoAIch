from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CoAIch Training Lab"
    DATABASE_URL: PostgresDsn = Field(..., env="DATABASE_URL")
    PARSER_VERSION: str = "1.0"
    API_USERNAME: str = Field(..., env="API_USERNAME")
    API_PASSWORD: str = Field(..., env="API_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
