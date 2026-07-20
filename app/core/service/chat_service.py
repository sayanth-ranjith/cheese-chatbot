# app/application/chat_service.py

from app.core.abstract.LanguageModel import LanguageModel
from app.schemas.ChatModels import ChatRequest, ChatResponse


class ChatService:

    def __init__(self, language_model: LanguageModel) -> None:
        self._language_model = language_model

    async def ask(self, request: ChatRequest) -> ChatResponse:
        answer = await self._language_model.generate(request.message)

        return ChatResponse(
            message_id=request.message_id,
            response=answer,
        )