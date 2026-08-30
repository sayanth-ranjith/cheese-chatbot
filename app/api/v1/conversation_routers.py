# app/api/v1/conversation_routers.py

from fastapi import APIRouter, status

from app.core.auth_config import CurrentUserDependency
from app.core.conversation_config import ConversationServiceDependency
from app.schemas.ConversationModels import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationSummary,
    MessageOut,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListResponse, status_code=status.HTTP_200_OK)
async def list_conversations(
    current_user: CurrentUserDependency,
    conversation_service: ConversationServiceDependency,
) -> ConversationListResponse:
    conversations = await conversation_service.list_conversations(current_user.id)

    return ConversationListResponse(
        conversations=[
            ConversationSummary(
                conversation_id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )
            for conversation in conversations
        ]
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUserDependency,
    conversation_service: ConversationServiceDependency,
) -> ConversationDetailResponse:
    conversation, messages = await conversation_service.get_conversation(
        current_user.id, conversation_id
    )

    return ConversationDetailResponse(
        conversation_id=conversation.id,
        title=conversation.title,
        messages=[
            MessageOut(role=m.role, content=m.content, created_at=m.created_at)
            for m in messages
        ],
    )
