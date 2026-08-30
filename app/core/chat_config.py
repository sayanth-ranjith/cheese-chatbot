# app/api/dependencies/chat.py

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.abstract.LanguageModel import LanguageModel
from app.core.config import Settings, get_settings
from app.core.embedding_config import get_embedding_model
from app.core.embedding_model.embedding_model import EmbeddingModel
from app.core.knowledge_base_config import get_vector_store
from app.core.llm.groq_language_model import GroqLanguageModel
from app.core.service.chat_service import ChatService
from app.core.service.retrieval_service import RetrievalService
from app.core.vector_store.vector_store import VectorStore


@lru_cache
def get_language_model() -> LanguageModel:
    settings: Settings = get_settings()

    return GroqLanguageModel(
        api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=0,
    )


def get_retrieval_service(
    embedding_model: Annotated[EmbeddingModel, Depends(get_embedding_model)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> RetrievalService:
    return RetrievalService(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )


def get_chat_service(
    language_model: Annotated[
        LanguageModel,
        Depends(get_language_model),
    ],
    retrieval_service: Annotated[
        RetrievalService,
        Depends(get_retrieval_service),
    ],
) -> ChatService:
    settings: Settings = get_settings()

    return ChatService(
        language_model=language_model,
        retrieval_service=retrieval_service,
        top_k=settings.retrieval_top_k,
    )


ChatServiceDependency = Annotated[
    ChatService,
    Depends(get_chat_service),
]