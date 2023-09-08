import secrets
from functools import cached_property

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    FieldValidationInfo,
    PostgresDsn,
    computed_field,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str
    server_host: AnyHttpUrl
    cors_origins: list[AnyHttpUrl] = []

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
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_server,
                path=f"/{self.postgres_db}",
            )
        )

    smtp_tls: bool = True
    smtp_host: str = ""
    smtp_port: int = 0
    smtp_user: str = ""
    smtp_password: str = ""
    emails_from_email: EmailStr | None = None
    emails_from_name: str = ""

    @field_validator("emails_from_name")
    @classmethod
    def get_project_name(cls, v: str, info: FieldValidationInfo) -> str:
        if not v:
            return info.data["project_name"]

        return v

    @computed_field  # type: ignore[misc]
    @cached_property
    def emails_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_port and self.emails_from_email)

    email_reset_token_expire_hours: int = 48
    first_superuser: EmailStr
    first_superuser_password: str
    users_open_registration: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
