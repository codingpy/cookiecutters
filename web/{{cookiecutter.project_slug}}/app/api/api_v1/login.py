from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, crud, schemas
from app.api import deps

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
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

    return {"access_token": auth.create_access_token(user.id, form_data.scopes)}
