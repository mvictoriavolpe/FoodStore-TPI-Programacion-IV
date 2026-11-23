from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator


class UserCreate(SQLModel):
    username: str = Field(min_length=3)
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def bcrypt_limit(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña admite como máximo 72 bytes UTF-8")
        return value

    @field_validator("username", "full_name", mode="before")
    @classmethod
    def non_blank(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("El campo no puede estar vacío")
        return value.strip()


class UserPublic(SQLModel):
    id: int
    username: str
    full_name: str
    email: str
    role: str
    disabled: bool
    created_at: datetime
