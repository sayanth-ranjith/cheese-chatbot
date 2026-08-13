# app/api/v1/embedding_routers.py

from fastapi import APIRouter, status

from app.core.embedding_config import EmbeddingServiceDependency
from app.schemas.EmbeddingModels import EmbeddingRequest, EmbeddingResponse

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


@router.post("", response_model=EmbeddingResponse, status_code=status.HTTP_200_OK,)
async def create_embeddings(
    request: EmbeddingRequest,
    embedding_service: EmbeddingServiceDependency,
) -> EmbeddingResponse:
    return await embedding_service.embed(request)
