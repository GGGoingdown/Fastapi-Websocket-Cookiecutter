import pytest
from httpx import AsyncClient
from unittest import mock

# Application
from app import services, repositories
from app.constants.error_codes import ERROR_CODES
from app.schemas import AuthSchema

# Tests
from tests import test_utils

ENDPOINT = "/auth/login"


@pytest.mark.login
@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    fake_user = test_utils.fake_guest_user()
    data = {"username": fake_user.email, "password": fake_user.password}
    res = await client.post(ENDPOINT, data=data)
    assert res.status_code == 200, f"Error status code: {res.status_code}, Expected 200"

    # Validation
    AuthSchema.LoginResponse(**res.json())


@pytest.mark.login
@pytest.mark.asyncio
async def test_login_401_incorrect_username_or_password_error(client: AsyncClient):
    data = {"username": "hello", "password": "hello"}
    res = await client.post(ENDPOINT, data=data)
    assert res.status_code == 401, f"Error status code: {res.status_code}, Expected 401"

    assert res.json() == {
        "detail": "Incorrect username or password"
    }, f"Unexepcted response: {res.json()}"


@pytest.mark.login
@pytest.mark.asyncio
async def test_login_401_inactive_account_error(client: AsyncClient, app):
    # Fake data
    fake_user = test_utils.fake_guest_user()
    user_in_db = await test_utils.mock_user_in_db(name="guest")
    user_in_db.is_active = False

    # Mock authentication service
    authentication_service_mock = mock.AsyncMock(spec=services.AuthenticationService)
    authentication_service_mock.authenticate_user.return_value = user_in_db
    with app.container.services.authentication_service.override(
        authentication_service_mock
    ):
        data = {"username": fake_user.email, "password": fake_user.password}
        res = await client.post(ENDPOINT, data=data)

    assert res.status_code == 401, f"Error status code: {res.status_code}, Expected 401"

    assert res.json() == {
        "detail": "Inactive account"
    }, f"Unexepcted response: {res.json()}"

    authentication_service_mock.authenticate_user.assert_called_once()


@pytest.mark.login
@pytest.mark.asyncio
async def test_login_500_save_cache_error(client: AsyncClient, app):
    fake_user = test_utils.fake_guest_user()

    # Mock user cache
    user_cache_mock = mock.AsyncMock(spec=repositories.UserCache)
    user_cache_mock.save.return_value = False

    with app.container.services.user_cache.override(user_cache_mock):
        data = {"username": fake_user.email, "password": fake_user.password}
        res = await client.post(ENDPOINT, data=data)

    assert res.status_code == 500, f"Error status code: {res.status_code}, Expected 500"

    assert res.json() == {"detail": f"Error code: {ERROR_CODES.SAVE_CACHE_ERROR.code}"}

    user_cache_mock.save.assert_called_once()
