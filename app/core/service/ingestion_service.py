# app/core/service/ingestion_service.py

from fastapi.concurrency import run_in_threadpool

from app.core.document_loader.document_loader import DocumentLoader
from app.core.document_splitter.document_splitter import DocumentSplitter
from app.core.embedding_model.embedding_model import EmbeddingModel
from app.core.vector_store.vector_store import VectorStore
from app.schemas.KnowledgeBaseModels import IngestedChunk, IngestResponse


class IngestionService:

    def __init__(
        self,
        loader: DocumentLoader,
        splitter: DocumentSplitter,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        self._loader = loader
        self._splitter = splitter
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    async def ingest(self) -> IngestResponse:
        documents = await run_in_threadpool(self._loader.load)
        chunks = self._splitter.split(documents)

        embeddings = await run_in_threadpool(
            self._embedding_model.embed_documents,
            chunks,
        )

        ingested_chunks = [
            IngestedChunk(
                content=chunk.content,
                metadata=chunk.metadata,
                embedding=embedding,
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        await run_in_threadpool(
            self._vector_store.add_documents,
            ingested_chunks,
        )

        return IngestResponse(
            documents_loaded=len(documents),
            chunks_created=len(chunks),
            model=self._embedding_model.model_name,
            chunks=ingested_chunks,
        )
