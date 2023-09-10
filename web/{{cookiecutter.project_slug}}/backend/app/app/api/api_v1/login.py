from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, crud, schemas
from app.api import deps
from app.config import settings
from app.tasks import send_reset_password_email

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_for_access_token(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return {
        "access_token": auth.create_access_token(
            schemas.TokenData(user_id=user.id, scopes=set(form_data.scopes))
        )
    }


@router.post("/recover-password/{email}", response_model=schemas.Msg)
async def recover_password(
    db: Annotated[AsyncSession, Depends(deps.get_db)], email: EmailStr
) -> Any:
    """
    Password Recovery
    """
    user = await crud.user.get_by_email(db, email)
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system",
        )

    token_data = schemas.TokenData(user_id=user.id)
    reset_token = auth.create_access_token(
        token_data,
        expires_delta=timedelta(hours=settings.email_reset_token_expire_hours),
    )

    send_reset_password_email.delay(email, username=email, token=reset_token)

    return {"msg": "Password recovery email sent"}


@router.post("/reset-password", response_model=schemas.Msg)
async def reset_password(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    token: Annotated[str, Body()],
    new_password: Annotated[str, Body()],
) -> Any:
    """
    Reset password
    """
    token_data = auth.decode_access_token(token)
    if not token_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = await crud.user.get(db, token_data.user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    user_in = schemas.UserUpdate(password=new_password)
    await crud.user.update(db, user.id, user_in)

    return {"msg": "Password updated successfully"}
