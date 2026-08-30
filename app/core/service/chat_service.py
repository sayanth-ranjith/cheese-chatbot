# app/application/chat_service.py

from app.core.abstract.LanguageModel import LanguageModel
from app.core.service.retrieval_service import RetrievalService
from app.schemas.ChatModels import ChatRequest, ChatResponse


class ChatService:

    def __init__(
        self,
        language_model: LanguageModel,
        retrieval_service: RetrievalService,
        top_k: int = 5,
    ) -> None:
        self._language_model = language_model
        self._retrieval_service = retrieval_service
        self._top_k = top_k

    async def ask(self, request: ChatRequest) -> ChatResponse:
        results = await self._retrieval_service.retrieve(
            request.message,
            top_k=self._top_k,
        )

        context = "\n\n".join(result.content for result in results)

        answer = await self._language_model.generate(
            request.message,
            context=context,
        )

        sources = list(
            dict.fromkeys(
                result.metadata.get("file_name", result.metadata.get("source", "unknown"))
                for result in results
            )
        )

        return ChatResponse(
            message_id=request.message_id,
            response=answer,
            sources=sources,
        )