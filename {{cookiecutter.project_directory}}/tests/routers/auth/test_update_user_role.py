import pytest
from httpx import AsyncClient
from unittest import mock

# Application
from app import repositories
from app.security import get_current_user_in_cache
from app.constants import RoleEnum
from app.schemas import UserSchema

# Tests
from tests import test_utils


ENDPOINT = "/auth/user-role"


@pytest.mark.user_role
@pytest.mark.asyncio
async def test_update_user_role(client: AsyncClient, app):
    # Override dependency
    app.dependency_overrides[
        get_current_user_in_cache
    ] = test_utils.override_get_current_user_in_cache_user_super
    # Create payload
    payload = UserSchema.UserMail(email="hello@gmail.com").dict()
    # Fake user model
    fake_user_model = await test_utils.mock_user_model()
    # Mock user reposityr
    user_repo_mock = mock.AsyncMock(spec=repositories.UserRepo)
    user_repo_mock.get_by_mail.return_value = fake_user_model
    user_repo_mock.add_roles.return_value = None

    with app.container.services.user_repo.override(user_repo_mock):
        res = await client.put(ENDPOINT, json=payload)

    assert res.status_code == 200, f"Error stauts code: {res.status_code}"

    assert res.json() == {
        "detail": "Update user permission success"
    }, f"Unexpected response: {res.json()}"

    user_repo_mock.get_by_mail.assert_called_once()
    user_repo_mock.add_roles.assert_called_once()


@pytest.mark.user_role
@pytest.mark.asyncio
async def test_update_user_role_401_authentication_error(client: AsyncClient):
    # Guest headers
    headers = test_utils.create_headers(RoleEnum.GUEST)
    payload = UserSchema.UserMail(email="hello@gmail.com").dict()
    res = await client.put(ENDPOINT, json=payload, headers=headers)

    assert res.status_code == 403, f"Error status code: {res.status_code}"

    assert res.json() == {
        "detail": "Not enough permissions"
    }, f"Unexpected response: {res.json()}"


@pytest.mark.user_role
@pytest.mark.asyncio
async def test_update_user_role_404_mail_not_found_error(client: AsyncClient, app):
    app.dependency_overrides[
        get_current_user_in_cache
    ] = test_utils.override_get_current_user_in_cache_user_super

    user_repo_mock = mock.AsyncMock(spec=repositories.UserRepo)
    user_repo_mock.get_by_mail.return_value = None

    with app.container.services.user_repo.override(user_repo_mock):
        payload = UserSchema.UserMail(email="hello@gmail.com").dict()
        res = await client.put(ENDPOINT, json=payload)

    assert res.status_code == 404, f"Error status code: {res.status_code}"

    assert res.json() == {
        "detail": "Email not found"
    }, f"Unexpected response: {res.json()}"

    user_repo_mock.get_by_mail.assert_called_once()
