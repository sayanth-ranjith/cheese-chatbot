# app/api/v1/auth_routers.py

from fastapi import APIRouter, status

from app.core.user_config import AuthServiceDependency
from app.schemas.AuthModels import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, auth_service: AuthServiceDependency) -> RegisterResponse:
    return await auth_service.register(request)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, auth_service: AuthServiceDependency) -> LoginResponse:
    return await auth_service.login(request)
