from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status

from app.core.dependencies import AccessTokenBearer, DbSession, RefreshTokenBearer
from app.users.schemas import UserRead, UserCreate
from app.users.service import UserService
from app.users.schemas import UserLogin, TokenResponse
from app.core.security import token_blocklist

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()


@router.post(
    "/signup",
    response_model=UserRead,
    summary="User Signup",
    status_code=status.HTTP_201_CREATED,
)
async def signup(db_session: DbSession, user_create: UserCreate) -> UserRead:
    return await UserService.create_user(db_session, user_create)


@router.post("/login", response_model=TokenResponse, summary="User Login")
async def login(
    db_session: DbSession, form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenResponse:

    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await UserService.login(db_session, login_data)


@router.get("/refresh", response_model=TokenResponse, summary="Refresh Access Token")
async def refresh_token(
    token_data: dict = Depends(refresh_token_bearer),
) -> TokenResponse:
    return await UserService.refresh_token(token_data)


@router.get("/logout", summary="Logout User")
async def revoke_token(
    token_data: dict = Depends(access_token_bearer),
) -> JSONResponse:
    jti = token_data.get("jti")
    token_blocklist.add(jti)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "logout successfully"},
    )
