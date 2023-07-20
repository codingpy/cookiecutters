from datetime import datetime, timedelta
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer

from app.config import settings


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenData(BaseModel):
    id: Annotated[int, PlainSerializer(lambda x: str(x))] = Field(alias="sub")
    scopes: Annotated[
        set[str],
        BeforeValidator(lambda x: x.split()),
        PlainSerializer(lambda x: " ".join(x)),
    ] = Field(alias="scope")
    exp: datetime = Field(
        default_factory=lambda: datetime.utcnow()
        + timedelta(minutes=settings.access_token_expire_minutes)
    )
