import pytest

from app.core.abstract.LanguageModel import LanguageModel
from app.core.service.chat_service import ChatService
from app.core.service.retrieval_service import RetrievalService
from app.core.vector_store.vector_store import VectorSearchResult
from app.schemas.ChatModels import ChatRequest


class FakeLanguageModel(LanguageModel):
    def __init__(self) -> None:
        self.last_message: str | None = None
        self.last_context: str | None = None

    async def generate(self, message: str, context: str = "") -> str:
        self.last_message = message
        self.last_context = context
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
        )
        request = ChatRequest(message_id="2", message="unrelated question")

        response = await service.ask(request)

        assert language_model.last_context == ""
        assert response.sources == []
