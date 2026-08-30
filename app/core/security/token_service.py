from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenPayload:
    subject: str
    expires_at: datetime


class TokenError(Exception):
    pass


class TokenService(ABC):

    @abstractmethod
    def issue(self, subject: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, token: str) -> TokenPayload:
        raise NotImplementedError
