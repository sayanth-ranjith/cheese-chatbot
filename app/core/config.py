from functools import lru_cache
from pathlib import Path

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
        default="openai/gpt-oss-120b",
        validation_alias="GROQ_MODEL"
    )

    # -------------------------------------------------
    # Jina
    # -------------------------------------------------

    jina_api_key: SecretStr = Field(
        validation_alias="JINA_API_KEY"
    )

    jina_model: str = Field(
        default="jina-embeddings-v3",
        validation_alias="JINA_MODEL"
    )

    # -------------------------------------------------
    # Knowledge base
    # -------------------------------------------------

    knowledge_base_dir: Path = Field(
        default=Path("app/knowledge_base"),
        validation_alias="KNOWLEDGE_BASE_DIR"
    )

    chunk_size: int = Field(
        default=1000,
        validation_alias="CHUNK_SIZE"
    )

    chunk_overlap: int = Field(
        default=200,
        validation_alias="CHUNK_OVERLAP"
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
