# app/core/conversation_config.py

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.conversation_store.conversation_store import ConversationStore
from app.core.conversation_store.mongodb_conversation_store import (
    MongoDBConversationStore,
)
from app.core.service.conversation_service import ConversationService


@lru_cache
def get_conversation_store() -> ConversationStore:
    settings: Settings = get_settings()

    return MongoDBConversationStore(
        uri=settings.mongodb_uri.get_secret_value(),
        db_name=settings.mongodb_db_name,
        conversations_collection_name=settings.mongodb_conversations_collection,
        messages_collection_name=settings.mongodb_messages_collection,
        retention_seconds=settings.conversation_retention_days * 24 * 60 * 60,
    )


def get_conversation_service(
    conversation_store: Annotated[ConversationStore, Depends(get_conversation_store)],
) -> ConversationService:
    return ConversationService(conversation_store=conversation_store)


ConversationServiceDependency = Annotated[
    ConversationService,
    Depends(get_conversation_service),
]
