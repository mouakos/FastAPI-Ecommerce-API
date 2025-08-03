from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(
        None, description="JWT refresh token, if applicable"
    )
    token_type: str = Field(default="Bearer", description="Type of the token")
    access_token_expires_in: int = Field(
        ..., description="Access token expiration time in seconds"
    )


class TokenData(BaseModel):
    sub: str
    jti: str
    role: str
    refresh: bool
    exp: int

    def get_uuid(self) -> UUID:
        return UUID(self.sub)

    def is_valid(self) -> bool:
        """
        Check if the token data is valid.
        Returns:
            bool: True if valid, False otherwise.
        """
        return (
            self.sub is not None
            and self.jti is not None
            and self.exp is not None
            and self.role is not None
            and self.refresh is not None
        )
