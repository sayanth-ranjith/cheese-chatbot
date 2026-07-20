from abc import ABC, abstractmethod


class LanguageModel(ABC):

    @abstractmethod
    async def generate(self, message: str) -> str:
        """Generate an answer for the provided message."""
        raise NotImplementedError