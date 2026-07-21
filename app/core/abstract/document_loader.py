from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Any


class DocumentLoader(ABC):
    @abstractmethod
    def load(self) -> list["Document"]:
        pass


@dataclass(frozen=True)
class Document:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)