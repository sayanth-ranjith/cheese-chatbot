from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: str
    email: str
    hashed_password: str
    created_at: datetime


class UserStore(ABC):

    @abstractmethod
    def create(self, email: str, hashed_password: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError
