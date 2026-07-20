from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.chat_routers import router as chat_router
from app.core.config import get_settings


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    application.include_router(health_router, prefix="/api/v1",)
    application.include_router(chat_router, prefix="/api/v1",)

    return application

#app = FastAPI()
app = create_application()