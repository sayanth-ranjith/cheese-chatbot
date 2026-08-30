# app/core/service/conversation_service.py

from fastapi.concurrency import run_in_threadpool

from app.core.conversation_store.conversation_store import (
    Conversation,
    ConversationMessage,
    ConversationStore,
    ensure_conversation_owned,
)


class ConversationService:

    def __init__(self, conversation_store: ConversationStore) -> None:
        self._conversation_store = conversation_store

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return await run_in_threadpool(self._conversation_store.list_conversations, user_id)

    async def get_conversation(
        self, user_id: str, conversation_id: str
    ) -> tuple[Conversation, list[ConversationMessage]]:
        conversation = await run_in_threadpool(
            self._conversation_store.get_conversation, conversation_id
        )
        conversation = ensure_conversation_owned(conversation, user_id)

        messages = await run_in_threadpool(
            self._conversation_store.get_messages, conversation_id, 1000
        )

        return conversation, messages
