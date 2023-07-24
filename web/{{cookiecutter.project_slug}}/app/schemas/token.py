from datetime import datetime
from typing import Annotated, Union

from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer


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
    exp: Union[datetime, None] = None
