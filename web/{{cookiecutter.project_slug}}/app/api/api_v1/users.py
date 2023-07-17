from typing import Annotated, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.config import settings

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def create_user(
    db: Annotated[AsyncSession, Depends(deps.get_db)], user_in: schemas.UserCreate
) -> models.User:
    """
    Create new user.
    """
    if await crud.user.exists_email(db, user_in.email):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system",
        )

    user = await crud.user.create(db, user_in)

    if settings.email_enabled:
        send_new_account_email(user.email)

    return user


@router.post("/open", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user_open(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    email: Annotated[EmailStr, Body()],
    password: Annotated[str, Body()],
    full_name: Annotated[Union[str, None], Body()] = None,
) -> models.User:
    """
    Create new user without the need to be logged in.
    """
    if not settings.users_open_registration:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Open user registration is forbidden on this server",
        )

    if await crud.user.exists_email(db, email):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system",
        )

    user_in = schemas.UserCreate(email=email, password=password, full_name=full_name)
    return await crud.user.create(db, user_in)


@router.get(
    "/",
    response_model=list[schemas.User],
    dependencies=[Depends(deps.get_current_active_superuser)],
    responses={204: {}},
)
async def read_users(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    response: Response,
    skip_id: int = 0,
    limit: int = 100,
) -> list[models.User]:
    """
    Retrieve users.
    """
    users = await crud.user.get_list(db, skip_id, limit)

    if not users:
        response.status_code = status.HTTP_204_NO_CONTENT

    return users


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)]
) -> models.User:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
    user_id: int,
) -> models.User:
    """
    Get a specific user by id.
    """
    if current_user.id == user_id:
        return current_user

    if not current_user.is_superuser:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges",
        )

    return await crud.user.get(db, user_id)


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[models.User, Depends(deps.get_current_active_user)],
    email: Annotated[Union[EmailStr, None], Body()] = None,
    password: Annotated[Union[str, None], Body()] = None,
    full_name: Annotated[Union[str, None], Body()] = None,
) -> models.User:
    """
    Update own user.
    """
    user_in = schemas.UserUpdate.model_validate(current_user)

    if email is not None:
        user_in.email = email
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name

    return await crud.user.update(db, current_user.id, user_in)


@router.put(
    "/{user_id}",
    response_model=schemas.User,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def update_user(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    user_id: int,
    user_in: schemas.UserUpdate,
) -> models.User:
    """
    Update a user.
    """
    if not await crud.user.exists(db, user_id):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system",
        )

    return await crud.user.update(db, user_id, user_in)


def send_new_account_email(to: str) -> None:
    pass
