from typing import Union

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: Union[EmailStr, None] = None
    full_name: Union[str, None] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Union[str, None] = None


class UserInDBBase(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
