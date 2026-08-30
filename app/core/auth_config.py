# app/core/auth_config.py

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security.token_service import TokenError, TokenService
from app.core.security_config import get_token_service
from app.core.user_config import get_user_store
from app.core.user_store.user_store import UserStore

_bearer_scheme = HTTPBearer(auto_error=False)

_INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str


async def _authenticate(
    credentials: HTTPAuthorizationCredentials,
    token_service: TokenService,
    user_store: UserStore,
) -> AuthenticatedUser:
    try:
        payload = await run_in_threadpool(token_service.verify, credentials.credentials)
    except TokenError:
        raise _INVALID_TOKEN_EXCEPTION

    user = await run_in_threadpool(user_store.get_by_id, payload.subject)
    if user is None:
        raise _INVALID_TOKEN_EXCEPTION

    return AuthenticatedUser(id=user.id, email=user.email)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer_scheme)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_store: Annotated[UserStore, Depends(get_user_store)],
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return await _authenticate(credentials, token_service, user_store)


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer_scheme)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_store: Annotated[UserStore, Depends(get_user_store)],
) -> AuthenticatedUser | None:
    if credentials is None:
        return None

    return await _authenticate(credentials, token_service, user_store)


CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
OptionalCurrentUserDependency = Annotated[
    AuthenticatedUser | None, Depends(get_optional_current_user)
]
