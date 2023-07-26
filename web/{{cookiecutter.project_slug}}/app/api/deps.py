from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, crud, models
from app.config import settings
from app.db import async_session

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_str}/login/access-token",
    scopes={"me": "Read information about the current user."},
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session.begin() as session:
        yield session


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    authenticate_value = "Bearer"
    if security_scopes.scopes:
        authenticate_value += f' scope="{security_scopes.scope_str}"'

    token_data = auth.decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

    user = await crud.user.get(db, token_data.id)
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": authenticate_value},
        )

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    user: Annotated[models.User, Security(get_current_user, scopes=["me"])]
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
