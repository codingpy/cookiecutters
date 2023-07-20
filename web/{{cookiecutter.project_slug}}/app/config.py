import secrets

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_v1_str: str = "/api/v1"
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 8 * 24 * 60

    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_database_uri(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_server,
            path=f"/{self.postgres_db}",
        )

    email_enabled: bool = False
    users_open_registration: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
