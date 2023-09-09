import pytest
from httpx import AsyncClient

from app.config import settings

# This is the same as using the @pytest.mark.anyio on all test functions in the module
pytestmark = pytest.mark.anyio


async def test_get_users_superuser_me(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.api_v1_str}/users/me", headers=superuser_token_headers
    )
    current_user = r.json()
    assert current_user["email"] == settings.first_superuser
    assert current_user["is_active"]
    assert current_user["is_superuser"]
