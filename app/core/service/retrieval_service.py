# app/core/service/retrieval_service.py

from fastapi.concurrency import run_in_threadpool

from app.core.embedding_model.embedding_model import EmbeddingModel
from app.core.vector_store.vector_store import VectorSearchResult, VectorStore


class RetrievalService:

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        query_embedding = await run_in_threadpool(
            self._embedding_model.embed_query,
            query,
        )

        return await run_in_threadpool(
            self._vector_store.similarity_search,
            query_embedding,
            top_k,
        )
