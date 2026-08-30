from abc import ABC, abstractmethod


class LanguageModel(ABC):

    @abstractmethod
    async def generate(self, message: str, context: str = "") -> str:
        """Generate an answer for the provided message, grounded in context."""
        raise NotImplementedError