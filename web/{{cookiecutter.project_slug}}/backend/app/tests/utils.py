from typing import TYPE_CHECKING

from app.config import settings

if TYPE_CHECKING:
    from httpx import AsyncClient


async def get_user_token_headers(
    client: "AsyncClient", email: str, password: str
) -> dict[str, str]:
    r = await client.post(
        f"{settings.api_v1_str}/login/access-token",
        data={"username": email, "password": password},
    )
    content = r.json()

    return {"Authorization": f"Bearer {content['access_token']}"}


async def get_superuser_token_headers(client: "AsyncClient") -> dict[str, str]:
    return await get_user_token_headers(
        client, settings.first_superuser, settings.first_superuser_password
    )
