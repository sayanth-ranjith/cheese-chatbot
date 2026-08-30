# app/core/service/auth_service.py

from app.core.security.password_hasher import PasswordHasher
from app.core.security.token_service import TokenService
from app.core.user_store.user_store import UserStore
from app.schemas.AuthModels import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:

    def __init__(
        self,
        user_store: UserStore,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        expires_minutes: int = 10080,
    ) -> None:
        self._user_store = user_store
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._expires_minutes = expires_minutes

    def register(self, request: RegisterRequest) -> RegisterResponse:
        email = request.email.lower()

        if self._user_store.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError(f"Email already registered: {email}")

        hashed_password = self._password_hasher.hash(request.password)
        user = self._user_store.create(email, hashed_password)

        return RegisterResponse(user_id=user.id, email=user.email)

    def login(self, request: LoginRequest) -> LoginResponse:
        email = request.email.lower()
        user = self._user_store.get_by_email(email)

        if user is None or not self._password_hasher.verify(
            request.password, user.hashed_password
        ):
            raise InvalidCredentialsError("Incorrect email or password")

        access_token = self._token_service.issue(user.id)

        return LoginResponse(
            access_token=access_token,
            expires_in=self._expires_minutes * 60,
        )
