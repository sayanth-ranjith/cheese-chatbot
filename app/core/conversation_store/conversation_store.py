from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Conversation:
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str
    created_at: datetime


class ConversationNotFoundError(Exception):
    pass


class ConversationStore(ABC):

    @abstractmethod
    def create_conversation(self, user_id: str, title: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Conversation | None:
        raise NotImplementedError

    @abstractmethod
    def list_conversations(self, user_id: str) -> list[Conversation]:
        raise NotImplementedError

    @abstractmethod
    def append_message(self, conversation_id: str, role: str, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, conversation_id: str, limit: int) -> list[ConversationMessage]:
        raise NotImplementedError


def ensure_conversation_owned(conversation: Conversation | None, user_id: str) -> Conversation:
    """Raises ConversationNotFoundError for both "doesn't exist" and "belongs
    to someone else" — deliberately collapsed so a non-owner can't tell the
    two apart (a distinct "forbidden" response would confirm the id is real)."""
    if conversation is None or conversation.user_id != user_id:
        raise ConversationNotFoundError("Conversation not found")

    return conversation
