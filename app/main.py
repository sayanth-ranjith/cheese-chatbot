from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.v1.auth_routers import router as auth_router
from app.api.v1.conversation_routers import router as conversation_router
from app.api.v1.health import router as health_router
from app.api.v1.chat_routers import router as chat_router
from app.api.v1.embedding_routers import router as embedding_router
from app.api.v1.knowledge_base_routers import router as knowledge_base_router
from app.core.config import get_settings
from app.core.conversation_store.conversation_store import ConversationNotFoundError
from app.core.service.auth_service import EmailAlreadyRegisteredError, InvalidCredentialsError


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    application.include_router(health_router, prefix="/api/v1",)
    application.include_router(auth_router, prefix="/api/v1",)
    application.include_router(conversation_router, prefix="/api/v1",)
    application.include_router(chat_router, prefix="/api/v1",)
    application.include_router(embedding_router, prefix="/api/v1",)
    application.include_router(knowledge_base_router, prefix="/api/v1",)

    @application.exception_handler(EmailAlreadyRegisteredError)
    async def handle_email_already_registered(
        request: Request, exc: EmailAlreadyRegisteredError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @application.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @application.exception_handler(ConversationNotFoundError)
    async def handle_conversation_not_found(
        request: Request, exc: ConversationNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    return application

#app = FastAPI()
app = create_application()