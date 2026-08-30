# app/application/chat_service.py

from fastapi.concurrency import run_in_threadpool

from app.core.abstract.LanguageModel import ConversationTurn, LanguageModel
from app.core.conversation_store.conversation_store import (
    ConversationStore,
    ensure_conversation_owned,
)
from app.core.service.retrieval_service import RetrievalService
from app.schemas.ChatModels import ChatRequest, ChatResponse

_TITLE_MAX_LENGTH = 60


class ChatService:

    def __init__(
        self,
        language_model: LanguageModel,
        retrieval_service: RetrievalService,
        conversation_store: ConversationStore,
        top_k: int = 5,
        history_limit: int = 10,
    ) -> None:
        self._language_model = language_model
        self._retrieval_service = retrieval_service
        self._conversation_store = conversation_store
        self._top_k = top_k
        self._history_limit = history_limit

    async def ask(self, request: ChatRequest, user_id: str | None = None) -> ChatResponse:
        conversation_id = await self._resolve_conversation_id(request, user_id)
        history = await self._load_history(conversation_id)

        results = await self._retrieval_service.retrieve(
            request.message,
            top_k=self._top_k,
        )

        context = "\n\n".join(result.content for result in results)

        answer = await self._language_model.generate(
            request.message,
            context=context,
            history=history,
        )

        if conversation_id is not None:
            await run_in_threadpool(
                self._conversation_store.append_message,
                conversation_id,
                "user",
                request.message,
            )
            await run_in_threadpool(
                self._conversation_store.append_message,
                conversation_id,
                "assistant",
                answer,
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
            conversation_id=conversation_id,
        )

    async def _resolve_conversation_id(
        self, request: ChatRequest, user_id: str | None
    ) -> str | None:
        if user_id is None:
            return None

        if request.conversation_id is not None:
            conversation = await run_in_threadpool(
                self._conversation_store.get_conversation, request.conversation_id
            )
            ensure_conversation_owned(conversation, user_id)
            return request.conversation_id

        title = request.message[:_TITLE_MAX_LENGTH]
        if len(request.message) > _TITLE_MAX_LENGTH:
            title += "…"

        return await run_in_threadpool(
            self._conversation_store.create_conversation, user_id, title
        )

    async def _load_history(self, conversation_id: str | None) -> list[ConversationTurn]:
        if conversation_id is None:
            return []

        messages = await run_in_threadpool(
            self._conversation_store.get_messages, conversation_id, self._history_limit
        )

        return [ConversationTurn(role=m.role, content=m.content) for m in messages]