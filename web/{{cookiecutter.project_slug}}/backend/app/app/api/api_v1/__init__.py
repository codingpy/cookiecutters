from enum import Enum

from fastapi import APIRouter

from app.api.api_v1 import login, users


class Tags(Enum):
    LOGIN = "login"
    USERS = "users"


router = APIRouter()
router.include_router(login.router, tags=[Tags.LOGIN])
router.include_router(users.router, prefix="/users", tags=[Tags.USERS])
