from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.schemas import UserCreate, UserLogin, UserRead, TokenResponse
from src.auth.service import AuthService
from src.database.core import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "/signup",
    response_model=UserRead,
    summary="User Signup",
    status_code=status.HTTP_201_CREATED,
)
async def signup(db_session: DbSession, user_create: UserCreate) -> UserRead:
    return await AuthService.signup(db_session, user_create)


@router.post("/login", response_model=TokenResponse, summary="User Login")
async def login(
    db_session: DbSession, form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenResponse:

    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await AuthService.login(db_session, login_data)
