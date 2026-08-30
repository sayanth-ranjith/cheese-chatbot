from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationTurn:
    role: str
    content: str


class LanguageModel(ABC):

    @abstractmethod
    async def generate(
        self,
        message: str,
        context: str = "",
        history: list[ConversationTurn] | None = None,
    ) -> str:
        """Generate an answer for the provided message, grounded in context
        and optionally aware of prior conversation turns."""
        raise NotImplementedError