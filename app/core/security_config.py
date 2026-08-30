# app/core/security_config.py

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.core.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.core.security.password_hasher import PasswordHasher


@lru_cache
def get_password_hasher() -> PasswordHasher:
    settings: Settings = get_settings()

    return BcryptPasswordHasher(rounds=settings.bcrypt_rounds)
