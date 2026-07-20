# app/api/dependencies/chat.py

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.abstract.LanguageModel import LanguageModel
from app.core.config import Settings, get_settings
from app.core.llm.groq_language_model import GroqLanguageModel
from app.core.service.chat_service import ChatService


@lru_cache
def get_language_model() -> LanguageModel:
    settings: Settings = get_settings()

    return GroqLanguageModel(
        api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=0,
    )


def get_chat_service(
    language_model: Annotated[
        LanguageModel,
        Depends(get_language_model),
    ],
) -> ChatService:
    return ChatService(language_model=language_model)


ChatServiceDependency = Annotated[
    ChatService,
    Depends(get_chat_service),
]