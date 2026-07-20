from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    application: str
    version: str
    environment: str


@router.get(
    "",
    response_model=HealthResponse,
    summary="Check application health",
)
async def health_check(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )