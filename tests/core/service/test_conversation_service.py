from datetime import datetime, timezone

import pytest

from app.core.conversation_store.conversation_store import (
    Conversation,
    ConversationMessage,
    ConversationNotFoundError,
    ConversationStore,
)
from app.core.service.conversation_service import ConversationService


class FakeConversationStore(ConversationStore):
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._messages: dict[str, list[ConversationMessage]] = {}
        self._next_id = 1

    def create_conversation(self, user_id: str, title: str) -> str:
        conversation_id = str(self._next_id)
        self._next_id += 1
        now = datetime.now(timezone.utc)
        self._conversations[conversation_id] = Conversation(
            id=conversation_id,
            user_id=user_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self._messages[conversation_id] = []
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def list_conversations(self, user_id: str) -> list[Conversation]:
        return [c for c in self._conversations.values() if c.user_id == user_id]

    def append_message(self, conversation_id: str, role: str, content: str) -> None:
        self._messages[conversation_id].append(
            ConversationMessage(role=role, content=content, created_at=datetime.now(timezone.utc))
        )

    def get_messages(self, conversation_id: str, limit: int) -> list[ConversationMessage]:
        return self._messages.get(conversation_id, [])[-limit:]


class TestListConversations:
    @pytest.mark.asyncio
    async def test_only_returns_conversations_for_the_given_user(self):
        store = FakeConversationStore()
        service = ConversationService(store)
        store.create_conversation("user-a", "A's thread")
        store.create_conversation("user-b", "B's thread")

        result = await service.list_conversations("user-a")

        assert len(result) == 1
        assert result[0].title == "A's thread"


class TestGetConversation:
    @pytest.mark.asyncio
    async def test_returns_conversation_and_messages_for_the_owner(self):
        store = FakeConversationStore()
        service = ConversationService(store)
        conversation_id = store.create_conversation("user-a", "A's thread")
        store.append_message(conversation_id, "user", "hi")

        conversation, messages = await service.get_conversation("user-a", conversation_id)

        assert conversation.id == conversation_id
        assert [m.content for m in messages] == ["hi"]

    @pytest.mark.asyncio
    async def test_missing_conversation_raises(self):
        store = FakeConversationStore()
        service = ConversationService(store)

        with pytest.raises(ConversationNotFoundError):
            await service.get_conversation("user-a", "does-not-exist")

    @pytest.mark.asyncio
    async def test_another_users_conversation_raises(self):
        store = FakeConversationStore()
        service = ConversationService(store)
        conversation_id = store.create_conversation("user-a", "A's thread")

        with pytest.raises(ConversationNotFoundError):
            await service.get_conversation("user-b", conversation_id)
