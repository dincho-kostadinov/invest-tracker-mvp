import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def _password_byte_length(cls, value: str) -> str:
        # bcrypt's limit is 72 *bytes*, not characters — see
        # app/core/security.py.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ExchangeRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None
