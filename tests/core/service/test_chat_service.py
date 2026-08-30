from datetime import datetime, timezone

import pytest

from app.core.abstract.LanguageModel import ConversationTurn, LanguageModel
from app.core.conversation_store.conversation_store import (
    Conversation,
    ConversationMessage,
    ConversationNotFoundError,
    ConversationStore,
)
from app.core.service.chat_service import ChatService
from app.core.service.retrieval_service import RetrievalService
from app.core.vector_store.vector_store import VectorSearchResult
from app.schemas.ChatModels import ChatRequest


class FakeLanguageModel(LanguageModel):
    def __init__(self) -> None:
        self.last_message: str | None = None
        self.last_context: str | None = None
        self.last_history: list[ConversationTurn] | None = None

    async def generate(
        self,
        message: str,
        context: str = "",
        history: list[ConversationTurn] | None = None,
    ) -> str:
        self.last_message = message
        self.last_context = context
        self.last_history = history
        return f"answer to: {message}"


class FakeRetrievalService(RetrievalService):
    def __init__(self, results: list[VectorSearchResult]) -> None:
        self._results = results
        self.last_query: str | None = None
        self.last_top_k: int | None = None

    async def retrieve(self, query: str, top_k: int = 5) -> list[VectorSearchResult]:
        self.last_query = query
        self.last_top_k = top_k
        return self._results


class FakeConversationStore(ConversationStore):
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._messages: dict[str, list[ConversationMessage]] = {}
        self._next_id = 1
        self.appended: list[tuple[str, str, str]] = []

    def create_conversation(self, user_id: str, title: str) -> str:
        conversation_id = str(self._next_id)
        self._next_id += 1
        now = datetime.now(timezone.utc)
        self._conversations[conversation_id] = Conversation(
            id=conversation_id, user_id=user_id, title=title, created_at=now, updated_at=now
        )
        self._messages[conversation_id] = []
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def list_conversations(self, user_id: str) -> list[Conversation]:
        return [c for c in self._conversations.values() if c.user_id == user_id]

    def append_message(self, conversation_id: str, role: str, content: str) -> None:
        self.appended.append((conversation_id, role, content))
        self._messages[conversation_id].append(
            ConversationMessage(role=role, content=content, created_at=datetime.now(timezone.utc))
        )

    def get_messages(self, conversation_id: str, limit: int) -> list[ConversationMessage]:
        return self._messages.get(conversation_id, [])[-limit:]


class TestAsk:
    @pytest.mark.asyncio
    async def test_grounds_answer_in_retrieved_context_and_returns_sources(self):
        results = [
            VectorSearchResult(content="chunk one", metadata={"file_name": "a.md"}, score=0.9),
            VectorSearchResult(content="chunk two", metadata={"file_name": "b.md"}, score=0.8),
        ]
        language_model = FakeLanguageModel()
        retrieval_service = FakeRetrievalService(results)
        service = ChatService(
            language_model=language_model,
            retrieval_service=retrieval_service,
            conversation_store=FakeConversationStore(),
            top_k=2,
        )
        request = ChatRequest(message_id="1", message="how does retry work?")

        response = await service.ask(request)

        assert retrieval_service.last_query == "how does retry work?"
        assert retrieval_service.last_top_k == 2
        assert language_model.last_context == "chunk one\n\nchunk two"
        assert response.response == "answer to: how does retry work?"
        assert response.message_id == "1"
        assert response.sources == ["a.md", "b.md"]

    @pytest.mark.asyncio
    async def test_no_results_produces_empty_context_and_sources(self):
        language_model = FakeLanguageModel()
        retrieval_service = FakeRetrievalService([])
        service = ChatService(
            language_model=language_model,
            retrieval_service=retrieval_service,
            conversation_store=FakeConversationStore(),
        )
        request = ChatRequest(message_id="2", message="unrelated question")

        response = await service.ask(request)

        assert language_model.last_context == ""
        assert response.sources == []

    @pytest.mark.asyncio
    async def test_anonymous_request_never_touches_conversation_store(self):
        conversation_store = FakeConversationStore()
        service = ChatService(
            language_model=FakeLanguageModel(),
            retrieval_service=FakeRetrievalService([]),
            conversation_store=conversation_store,
        )
        request = ChatRequest(message_id="3", message="hello")

        response = await service.ask(request, user_id=None)

        assert response.conversation_id is None
        assert conversation_store.appended == []

    @pytest.mark.asyncio
    async def test_authenticated_without_conversation_id_creates_one_and_persists_both_turns(
        self,
    ):
        conversation_store = FakeConversationStore()
        language_model = FakeLanguageModel()
        service = ChatService(
            language_model=language_model,
            retrieval_service=FakeRetrievalService([]),
            conversation_store=conversation_store,
        )
        request = ChatRequest(message_id="4", message="hello there")

        response = await service.ask(request, user_id="user-a")

        assert response.conversation_id is not None
        assert conversation_store.appended == [
            (response.conversation_id, "user", "hello there"),
            (response.conversation_id, "assistant", "answer to: hello there"),
        ]

    @pytest.mark.asyncio
    async def test_authenticated_with_owned_conversation_id_appends_and_feeds_history(self):
        conversation_store = FakeConversationStore()
        conversation_id = conversation_store.create_conversation("user-a", "Existing thread")
        conversation_store.append_message(conversation_id, "user", "earlier question")
        conversation_store.append_message(conversation_id, "assistant", "earlier answer")
        language_model = FakeLanguageModel()
        service = ChatService(
            language_model=language_model,
            retrieval_service=FakeRetrievalService([]),
            conversation_store=conversation_store,
        )
        request = ChatRequest(
            message_id="5", message="follow-up question", conversation_id=conversation_id
        )

        response = await service.ask(request, user_id="user-a")

        assert response.conversation_id == conversation_id
        assert language_model.last_history == [
            ConversationTurn(role="user", content="earlier question"),
            ConversationTurn(role="assistant", content="earlier answer"),
        ]
        assert conversation_store.appended[-2:] == [
            (conversation_id, "user", "follow-up question"),
            (conversation_id, "assistant", "answer to: follow-up question"),
        ]

    @pytest.mark.asyncio
    async def test_conversation_id_owned_by_another_user_raises(self):
        conversation_store = FakeConversationStore()
        conversation_id = conversation_store.create_conversation("user-a", "A's thread")
        service = ChatService(
            language_model=FakeLanguageModel(),
            retrieval_service=FakeRetrievalService([]),
            conversation_store=conversation_store,
        )
        request = ChatRequest(
            message_id="6", message="sneaky", conversation_id=conversation_id
        )

        with pytest.raises(ConversationNotFoundError):
            await service.ask(request, user_id="user-b")
