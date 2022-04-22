import pytest

# Application
from app import models

from app.schemas import UserSchema
from app.constants import RoleEnum
from app.security import get_current_user_in_cache

ENDPOINT = "/users/me"


async def override_get_current_user_in_cache():
    user = await models.User.get(name="guest")
    return UserSchema.UserWithRoles(
        id=user.id,
        roles=[RoleEnum.GUEST.value],
    )


@pytest.mark.users
@pytest.mark.asyncio
async def test_get_me(client, app):
    app.dependency_overrides[
        get_current_user_in_cache
    ] = override_get_current_user_in_cache

    res = await client.get(ENDPOINT)
    assert res.status_code == 200, f"Error status code: {res.status_code}"
    response = res.json()
    assert response["email"] == "guest@gmail.com", "Invalid email"
    assert response["roles"] == [RoleEnum.GUEST.value], "Invalid roles"


@pytest.mark.users
@pytest.mark.asyncio
async def test_get_me_401_authorization_error(client, app):
    app.dependency_overrides = {}
    res = await client.get(ENDPOINT)
    assert res.status_code == 401, f"Error status code: {res.status_code}"
    assert res.json() == {"detail": "Not authenticated"}, f"{res.json()}"
