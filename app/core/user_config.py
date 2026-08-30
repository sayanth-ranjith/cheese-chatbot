# app/core/user_config.py

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.security.password_hasher import PasswordHasher
from app.core.security.token_service import TokenService
from app.core.security_config import get_password_hasher, get_token_service
from app.core.service.auth_service import AuthService
from app.core.user_store.mongodb_user_store import MongoDBUserStore
from app.core.user_store.user_store import UserStore


@lru_cache
def get_user_store() -> UserStore:
    settings: Settings = get_settings()

    return MongoDBUserStore(
        uri=settings.mongodb_uri.get_secret_value(),
        db_name=settings.mongodb_db_name,
        collection_name=settings.mongodb_users_collection,
    )


def get_auth_service(
    user_store: Annotated[UserStore, Depends(get_user_store)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> AuthService:
    settings: Settings = get_settings()

    return AuthService(
        user_store=user_store,
        password_hasher=password_hasher,
        token_service=token_service,
        expires_minutes=settings.jwt_expires_minutes,
    )


AuthServiceDependency = Annotated[
    AuthService,
    Depends(get_auth_service),
]
