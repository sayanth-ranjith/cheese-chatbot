# app/core/security_config.py

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.core.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.core.security.jwt_token_service import JwtTokenService
from app.core.security.password_hasher import PasswordHasher
from app.core.security.token_service import TokenService


@lru_cache
def get_password_hasher() -> PasswordHasher:
    settings: Settings = get_settings()

    return BcryptPasswordHasher(rounds=settings.bcrypt_rounds)


@lru_cache
def get_token_service() -> TokenService:
    settings: Settings = get_settings()

    return JwtTokenService(
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        expires_minutes=settings.jwt_expires_minutes,
    )
