from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # -------------------------------------------------
    # Application
    # -------------------------------------------------

    app_name: str = "Cheese Chatbot"
    app_version: str = "0.1.0"
    environment: str = "local"
    debug: bool = False

    # -------------------------------------------------
    # Groq
    # -------------------------------------------------

    groq_api_key: SecretStr = Field(
        validation_alias="GROQ_API_KEY"
    )

    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias="GROQ_MODEL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    # The value is loaded from GROQ_API_KEY/.env at runtime.  Pydantic's
    # mypy plugin does not account for fields populated through aliases.
    return Settings()  # type: ignore[call-arg]
