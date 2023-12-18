from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr = Field(pattern=r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+.[a-z]+$")
    password: str = Field(min_length=6, max_length=10)


class UserCreateSchema(UserSchema):
    pass


class UserUpdateSchema(UserSchema):
    pass


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
