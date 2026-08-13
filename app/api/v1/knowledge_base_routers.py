# app/api/v1/knowledge_base_routers.py

from fastapi import APIRouter, status

from app.core.knowledge_base_config import IngestionServiceDependency
from app.schemas.KnowledgeBaseModels import IngestResponse

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK,)
async def ingest_knowledge_base(
    ingestion_service: IngestionServiceDependency,
) -> IngestResponse:
    return await ingestion_service.ingest()
