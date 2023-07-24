from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, crud, schemas
from app.api import deps
from app.config import settings

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
            schemas.TokenData(sub=user.id, scope=" ".join(form_data.scopes))
        )
    }


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
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

    token_data = schemas.TokenData(sub=user.id, scope="me")
    token = auth.create_access_token(
        token_data,
        expires_delta=timedelta(hours=settings.email_reset_token_expire_hours),
    )

    send_reset_password_email(user.email, token)

    return {"msg": "Password recovery email sent"}


def send_reset_password_email(to: str, token: str) -> None:
    pass
