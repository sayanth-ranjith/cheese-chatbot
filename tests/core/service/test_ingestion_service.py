import pytest

from app.core.document_loader.document_loader import Document, DocumentLoader
from app.core.document_splitter.document_splitter import DocumentSplitter
from app.core.embedding_model.embedding_model import EmbeddingModel
from app.core.service.ingestion_service import IngestionService
from app.core.vector_store.vector_store import VectorSearchResult, VectorStore
from app.schemas.KnowledgeBaseModels import IngestedChunk


class FakeDocumentLoader(DocumentLoader):
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents

    def load(self) -> list[Document]:
        return self._documents


class FakeDocumentSplitter(DocumentSplitter):
    def split(self, documents: list[Document]) -> list[Document]:
        return [
            Document(
                content=f"{document.content}-chunk{index}",
                metadata={**document.metadata, "chunk_index": index},
            )
            for document in documents
            for index in range(2)
        ]


class FakeEmbeddingModel(EmbeddingModel):
    @property
    def model_name(self) -> str:
        return "fake-model"

    def embed_documents(self, documents: list[Document]) -> list[list[float]]:
        return [[float(index)] for index, _ in enumerate(documents)]

    def embed_query(self, query: str) -> list[float]:
        return [0.0]


class FakeVectorStore(VectorStore):
    def __init__(self) -> None:
        self.added_chunks: list[IngestedChunk] = []

    def add_documents(self, chunks: list[IngestedChunk]) -> list[str]:
        self.added_chunks.extend(chunks)
        return [str(index) for index, _ in enumerate(chunks)]

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        return []


class TestIngest:
    @pytest.mark.asyncio
    async def test_wires_load_split_embed_into_response(self):
        documents = [Document(content="doc1", metadata={"source": "a.md"})]
        vector_store = FakeVectorStore()
        service = IngestionService(
            loader=FakeDocumentLoader(documents),
            splitter=FakeDocumentSplitter(),
            embedding_model=FakeEmbeddingModel(),
            vector_store=vector_store,
        )

        response = await service.ingest()

        assert response.documents_loaded == 1
        assert response.chunks_created == 2
        assert response.model == "fake-model"
        assert [chunk.content for chunk in response.chunks] == [
            "doc1-chunk0",
            "doc1-chunk1",
        ]
        assert [chunk.embedding for chunk in response.chunks] == [[0.0], [1.0]]
        assert response.chunks[0].metadata["source"] == "a.md"
        assert len(vector_store.added_chunks) == 2

    @pytest.mark.asyncio
    async def test_no_documents_produces_empty_response(self):
        vector_store = FakeVectorStore()
        service = IngestionService(
            loader=FakeDocumentLoader([]),
            splitter=FakeDocumentSplitter(),
            embedding_model=FakeEmbeddingModel(),
            vector_store=vector_store,
        )

        response = await service.ingest()

        assert response.documents_loaded == 0
        assert response.chunks_created == 0
        assert response.chunks == []
        assert vector_store.added_chunks == []
