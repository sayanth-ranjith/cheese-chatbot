from fastapi import APIRouter, status

from app.core.auth_config import OptionalCurrentUserDependency
from app.core.chat_config import ChatServiceDependency
from app.schemas.ChatModels import ChatRequest, ChatResponse

router = APIRouter(prefix="/ask/cheese", tags=["cheese"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK,)
async def ask_question(
    request: ChatRequest,
    chat_service: ChatServiceDependency,
    current_user: OptionalCurrentUserDependency,
) -> ChatResponse:
    user_id = current_user.id if current_user else None
    return await chat_service.ask(request, user_id=user_id)