import pytest

# Application
from app.security import get_current_user_in_cache
from app.schemas import UserSchema
from app.constants import RoleEnum

# Testing
from tests import test_utils

ENDPOINT = "/users"


@pytest.mark.users
@pytest.mark.asyncio
async def test_get_all_users(client, app):
    app.dependency_overrides[
        get_current_user_in_cache
    ] = test_utils.override_get_current_user_in_cache_user_super
    res = await client.get(ENDPOINT)
    assert res.status_code == 200, f"Error status code: {res.status_code}"

    users = res.json()

    # Validation
    for user in users:
        UserSchema.UserInfo(**user)


@pytest.mark.users
@pytest.mark.asyncio
async def test_get_all_users_401_authentication_error(client, app):
    app.dependency_overrides = {}
    res = await client.get(
        ENDPOINT,
    )
    assert res.status_code == 401, f"Error status code: {res.status_code}"

    detail = res.json()
    assert detail == {"detail": "Not authenticated"}, f"{detail}"


@pytest.mark.users
@pytest.mark.asyncio
async def test_get_all_users_403_authentication_error(client, app):
    app.dependency_overrides = {}

    headers = test_utils.create_headers(RoleEnum.ADMIN)
    res = await client.get(ENDPOINT, headers=headers)

    # Not enough permission
    assert res.status_code == 403, f"Error status code: {res.status_code}, Expected 403"
    detail = res.json()
    assert detail == {"detail": "Not enough permissions"}, f"{detail}"
