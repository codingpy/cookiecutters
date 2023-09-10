from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.config import settings
from app.schemas import TokenData

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    token_data: TokenData, expires_delta: timedelta | None = None
) -> str:
    now = datetime.utcnow()

    if expires_delta:
        token_data.expires = now + expires_delta
    elif not token_data.expires:
        token_data.expires = now + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    return jwt.encode(token_data.model_dump(), settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData | None:
    try:
        return TokenData(
            **jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        )
    except (jwt.InvalidTokenError, ValidationError):
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
