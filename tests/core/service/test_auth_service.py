from datetime import datetime, timezone

import pytest

from app.core.security.password_hasher import PasswordHasher
from app.core.security.token_service import TokenPayload, TokenService
from app.core.service.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.core.user_store.user_store import User, UserStore
from app.schemas.AuthModels import LoginRequest, RegisterRequest


class FakeUserStore(UserStore):
    def __init__(self) -> None:
        self._users_by_email: dict[str, User] = {}
        self._next_id = 1

    def create(self, email: str, hashed_password: str) -> User:
        user = User(
            id=str(self._next_id),
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.now(timezone.utc),
        )
        self._next_id += 1
        self._users_by_email[email] = user
        return user

    def get_by_email(self, email: str) -> User | None:
        return self._users_by_email.get(email)

    def get_by_id(self, user_id: str) -> User | None:
        return next(
            (user for user in self._users_by_email.values() if user.id == user_id),
            None,
        )


class FakePasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, hashed: str) -> bool:
        return hashed == f"hashed:{password}"


class FakeTokenService(TokenService):
    def issue(self, subject: str) -> str:
        return f"token-for:{subject}"

    def verify(self, token: str) -> TokenPayload:
        raise NotImplementedError


class TestRegister:
    @pytest.mark.asyncio
    async def test_creates_a_user_with_a_hashed_password(self):
        user_store = FakeUserStore()
        service = AuthService(user_store, FakePasswordHasher(), FakeTokenService())

        response = await service.register(
            RegisterRequest(email="Person@Example.com", password="password123")
        )

        assert response.email == "person@example.com"
        stored = user_store.get_by_email("person@example.com")
        assert stored is not None
        assert stored.hashed_password == "hashed:password123"

    @pytest.mark.asyncio
    async def test_duplicate_email_raises(self):
        user_store = FakeUserStore()
        service = AuthService(user_store, FakePasswordHasher(), FakeTokenService())
        await service.register(
            RegisterRequest(email="person@example.com", password="password123")
        )

        with pytest.raises(EmailAlreadyRegisteredError):
            await service.register(
                RegisterRequest(email="person@example.com", password="different123")
            )


class TestLogin:
    @pytest.mark.asyncio
    async def test_returns_an_access_token_for_correct_credentials(self):
        user_store = FakeUserStore()
        service = AuthService(user_store, FakePasswordHasher(), FakeTokenService())
        await service.register(
            RegisterRequest(email="person@example.com", password="password123")
        )

        response = await service.login(
            LoginRequest(email="person@example.com", password="password123")
        )

        assert response.access_token.startswith("token-for:")
        assert response.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_wrong_password_raises(self):
        user_store = FakeUserStore()
        service = AuthService(user_store, FakePasswordHasher(), FakeTokenService())
        await service.register(
            RegisterRequest(email="person@example.com", password="password123")
        )

        with pytest.raises(InvalidCredentialsError):
            await service.login(LoginRequest(email="person@example.com", password="wrong"))

    @pytest.mark.asyncio
    async def test_unknown_email_raises(self):
        user_store = FakeUserStore()
        service = AuthService(user_store, FakePasswordHasher(), FakeTokenService())

        with pytest.raises(InvalidCredentialsError):
            await service.login(
                LoginRequest(email="nobody@example.com", password="password123")
            )
