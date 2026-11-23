from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./foodstore.db"
    SECRET_KEY: str = Field(
        default="cambiar-esta-clave-de-al-menos-32-caracteres", min_length=32
    )
    ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
