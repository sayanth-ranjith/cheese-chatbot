import pytest

from app.core.document_loader.document_loader import Document
from app.core.embedding_model.embedding_model import EmbeddingModel
from app.core.service.retrieval_service import RetrievalService
from app.core.vector_store.vector_store import VectorSearchResult, VectorStore
from app.schemas.KnowledgeBaseModels import IngestedChunk


class FakeEmbeddingModel(EmbeddingModel):
    @property
    def model_name(self) -> str:
        return "fake-model"

    def embed_documents(self, documents: list[Document]) -> list[list[float]]:
        return [[0.0] for _ in documents]

    def embed_query(self, query: str) -> list[float]:
        return [1.0, 0.0]


class FakeVectorStore(VectorStore):
    def __init__(self, results: list[VectorSearchResult]) -> None:
        self._results = results
        self.last_query_embedding: list[float] | None = None
        self.last_top_k: int | None = None

    def add_documents(self, chunks: list[IngestedChunk]) -> list[str]:
        return []

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        self.last_query_embedding = query_embedding
        self.last_top_k = top_k
        return self._results


class TestRetrieve:
    @pytest.mark.asyncio
    async def test_embeds_query_and_returns_search_results(self):
        expected = [VectorSearchResult(content="chunk1", metadata={"file_name": "a.md"}, score=0.9)]
        vector_store = FakeVectorStore(expected)
        service = RetrievalService(
            embedding_model=FakeEmbeddingModel(),
            vector_store=vector_store,
        )

        results = await service.retrieve("what is cheese retry?", top_k=3)

        assert results == expected
        assert vector_store.last_query_embedding == [1.0, 0.0]
        assert vector_store.last_top_k == 3
