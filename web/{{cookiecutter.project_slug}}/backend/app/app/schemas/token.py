from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_serializer


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenData(BaseModel):
    user_id: int
    expires: datetime | None = None
    scopes: set[str] = set()

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "sub": str(self.user_id),
            "exp": self.expires,
            "scope": " ".join(self.scopes),
        }
