from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr = Field(pattern=r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+.[a-z]+$")
    password: str = Field(min_length=6, max_length=10)


class UserCreateSchema(UserSchema):
    pass


class UserUpdateSchema(UserSchema):
    pass


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponseSchema(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    password: str = Field(min_length=6, max_length=10)


class ResetPasswordForm(ResetPassword): # TODO не получилось применить для получения форми
    # TODO new
    confirm_password: str = Field(min_length=6, max_length=10)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
