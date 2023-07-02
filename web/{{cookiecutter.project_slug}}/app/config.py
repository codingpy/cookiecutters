import secrets
from typing import Any, Union

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    api_v1_str: str = "/api/v1"
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 8 * 24 * 60

    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    sqlalchemy_database_uri: Union[PostgresDsn, None] = None

    @validator("sqlalchemy_database_uri", pre=True)
    def assemble_db_connection(cls, v: Union[str, None], values: dict[str, Any]) -> str:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values["postgres_user"],
            password=values["postgres_password"],
            host=values["postgres_server"],
            path=f"/{values['postgres_db']}",
        )

    class Config:
        env_file = ".env"


settings = Settings()
