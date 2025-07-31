from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status

from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.service import AuthService
from app.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from app.users.schemas import UserRead, UserCreate
from app.auth.schemas import TokenData, UserLogin, TokenResponse
from app.utils.security import token_blocklist
from app.database.core import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

refresh_token_bearer = RefreshTokenBearer()
DbSession = Annotated[AsyncSession, Depends(get_session)]
AccessToken = Annotated[TokenData, Depends(AccessTokenBearer())]


@router.post(
    "/signup",
    response_model=UserRead,
    summary="Signup",
    status_code=status.HTTP_201_CREATED,
)
async def signup(db_session: DbSession, user_create: UserCreate) -> UserRead:
    return await AuthService.register_user(db_session, user_create)


@router.post("/login", response_model=TokenResponse, summary="Login")
async def login(
    db_session: DbSession, form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenResponse:
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await AuthService.login(db_session, login_data)


@router.get("/refresh", response_model=TokenResponse, summary="Refresh Access Token")
async def refresh_token(
    token_data: TokenData = Depends(refresh_token_bearer),
) -> TokenResponse:
    return await AuthService.refresh_token(token_data)


@router.get("/logout", summary="Logout", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    token_data: AccessToken,
) -> None:
    jti = token_data.jti
    token_blocklist.add(jti)
