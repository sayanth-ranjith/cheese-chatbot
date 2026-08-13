# app/core/embedding_config.py

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.embedding_model.embedding_model import EmbeddingModel
from app.core.embedding_model.jina_embedding_model import JinaEmbeddingModel
from app.core.service.embedding_service import EmbeddingService


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    settings: Settings = get_settings()

    return JinaEmbeddingModel(
        api_key=settings.jina_api_key.get_secret_value(),
        model_name=settings.jina_model,
    )


def get_embedding_service(
    embedding_model: Annotated[
        EmbeddingModel,
        Depends(get_embedding_model),
    ],
) -> EmbeddingService:
    return EmbeddingService(embedding_model=embedding_model)


EmbeddingServiceDependency = Annotated[
    EmbeddingService,
    Depends(get_embedding_service),
]
