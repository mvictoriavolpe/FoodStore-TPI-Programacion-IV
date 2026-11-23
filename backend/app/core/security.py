from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return passwords.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    # bcrypt truncates at 72 bytes; reject rather than accepting an ambiguous password.
    return len(password.encode("utf-8")) <= 72 and passwords.verify(password, hashed)


def create_access_token(username: str) -> str:
    return jwt.encode(
        {
            "sub": username,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str):
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"require_exp": True, "require_sub": True},
    )
