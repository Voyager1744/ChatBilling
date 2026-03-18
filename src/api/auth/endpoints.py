from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse

from src.api.auth.dependencies import AuthServiceDependency, CurrentUserDependency
from src.api.auth.schemas import (
    LoginResponse,
    LoginRequest,
    RegisterRequest,
    UserResponseSchema,
)
from src.api.general_schemas import ErrorResponse, SussesResponse

router = APIRouter(prefix="/auth", tags=["authorization"])


@router.post("/login", response_model=LoginRequest)
async def login(
    service: AuthServiceDependency,
    data: LoginRequest = Body(),
) -> JSONResponse:
    user = await service.login(data.username, data.password)
    if not user:
        return JSONResponse(
            content=ErrorResponse(
                message="Пароль неверный или пользователь не существует"
            ).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return JSONResponse(
        content=LoginResponse.from_dto(user).model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.post("/register", response_model=SussesResponse)
async def register(
    service: AuthServiceDependency,
    data: RegisterRequest = Body(),
) -> JSONResponse:
    await service.register(data.name, data.username, data.password)
    return JSONResponse(
        content=SussesResponse(
            message="Пользователь успешно зарегистрирован"
        ).model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.get("/me", response_model=UserResponseSchema)
async def get_me(user: CurrentUserDependency) -> JSONResponse:
    if not user:
        return JSONResponse(
            content=ErrorResponse(message="Пользователь не авторизован").model_dump(),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return JSONResponse(
        content=UserResponseSchema.from_dto(user).model_dump(),
        status_code=status.HTTP_200_OK,
    )
