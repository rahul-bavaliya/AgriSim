from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr


class UserRegistrationResponse(BaseModel):
    success: bool
    message: str
    data: UserResponse
