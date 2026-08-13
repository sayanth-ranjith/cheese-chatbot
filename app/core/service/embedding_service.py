# app/core/service/embedding_service.py

from fastapi.concurrency import run_in_threadpool

from app.core.document_loader.document_loader import Document
from app.core.embedding_model.embedding_model import EmbeddingModel
from app.schemas.EmbeddingModels import EmbeddingRequest, EmbeddingResponse


class EmbeddingService:

    def __init__(self, embedding_model: EmbeddingModel) -> None:
        self._embedding_model = embedding_model

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        documents = [Document(content=text) for text in request.texts]

        vectors = await run_in_threadpool(
            self._embedding_model.embed_documents,
            documents,
        )

        dimensions = len(vectors[0]) if vectors else 0

        return EmbeddingResponse(
            model=self._embedding_model.model_name,
            dimensions=dimensions,
            embeddings=vectors,
        )
