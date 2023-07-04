from pydantic import BaseModel, Field, validator


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenData(BaseModel):
    id: int = Field(alias="sub")
    scopes: set[str] = Field(alias="scope")

    @validator("scopes", pre=True)
    def split_scope_str(cls, v: str) -> list[str]:
        return v.split()
