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
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    return jwt.encode(
        {
            "sub": str(token_data.user_id),
            "exp": datetime.utcnow() + expires_delta,
            "scope": " ".join(token_data.scopes),
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return TokenData(user_id=payload["sub"], scopes=payload["scope"].split())
    except (jwt.InvalidTokenError, ValidationError):
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
