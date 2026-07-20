from fastapi import APIRouter

from app.core.chat_config import ChatServiceDependency
from app.schemas.ChatModels import ChatRequest, ChatResponse

router = APIRouter(prefix="/ask/cheese", tags=["cheese"])

# app/api/v1/chat.py

from fastapi import APIRouter, status

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK,)
async def ask_question(request: ChatRequest, chat_service: ChatServiceDependency,) -> ChatResponse:
    return await chat_service.ask(request)