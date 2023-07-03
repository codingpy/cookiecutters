from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, crud, models, schemas
from app.config import settings
from app.db import async_session

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_str}/login/access-token",
    scopes={"me": "Read information about the current user."},
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    try:
        token_data = schemas.TokenData(
            **jwt.decode(token, settings.secret_key, algorithms=[auth.ALGORITHM])
        )
    except (JWTError, ValidationError):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    user = await crud.user.get(db, token_data.id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def get_current_active_user(
    user: Annotated[models.User, Depends(get_current_user)]
) -> models.User:
    if not user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user


async def get_current_active_superuser(
    user: Annotated[models.User, Depends(get_current_active_user)]
) -> models.User:
    if not user.is_superuser:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges",
        )

    return user
