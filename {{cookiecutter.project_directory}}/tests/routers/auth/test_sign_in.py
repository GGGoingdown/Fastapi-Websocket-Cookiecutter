import pytest
from httpx import AsyncClient
from unittest import mock

# Application
from app import services, repositories, exceptions
from app.constants.error_codes import ERROR_CODES
from app.schemas import AuthSchema, UserSchema

# Tests
from tests import test_utils


ENDPOINT = "/auth/sign-in"


@pytest.mark.signin
@pytest.mark.asyncio
async def test_sign_in(client: AsyncClient):
    data = UserSchema.UserCreate(
        email="hello@gmail.com", name="hello", password="hello", verify_password="hello"
    ).dict()

    res = await client.post(ENDPOINT, json=data)

    assert res.status_code == 200, f"Error status code: {res.status_code}"

    # Validation
    AuthSchema.SigninResponse(**res.json())


@pytest.mark.signin
@pytest.mark.asyncio
async def test_sign_in_409_conflict_error(client: AsyncClient, app):
    data = UserSchema.UserCreate(
        email="hello@gmail.com", name="hello", password="hello", verify_password="hello"
    ).dict()

    user_service_mock = mock.AsyncMock(spec=services.UserService)
    user_service_mock.create_user.side_effect = exceptions.SaveDBUserError(
        "hello@gmail.com"
    )

    with app.container.services.user_service.override(user_service_mock):
        res = await client.post(ENDPOINT, json=data)

    assert res.status_code == 409, f"Error status code: {res.status_code}, Expected 409"
    assert res.json() == {
        "detail": "Duplicate email"
    }, f"Unexpected response: {res.json()}"

    user_service_mock.create_user.assert_called_once()


@pytest.mark.signin
@pytest.mark.asyncio
async def test_sign_in_500_cache_data_error(client: AsyncClient, app):
    data = UserSchema.UserCreate(
        email="hello@gmail.com", name="hello", password="hello", verify_password="hello"
    ).dict()

    fake_user = await test_utils.mock_user_in_db(name="guest")

    # Mock auth cache
    auth_cache_mock = mock.AsyncMock(spec=repositories.AuthCache)
    auth_cache_mock.save_active_token.return_value = (False, "token")

    # Mock user service
    user_service_mock = mock.AsyncMock(spec=services.UserService)
    user_service_mock.create_user.return_value = fake_user

    with app.container.services.override_providers(
        auth_cache=auth_cache_mock, user_service=user_service_mock
    ):
        res = await client.post(ENDPOINT, json=data)

    assert res.status_code == 500, f"Error status code: {res.status_code}, Expected 500"

    assert res.json() == {"detail": f"Error code: {ERROR_CODES.SAVE_CACHE_ERROR.code}"}

    auth_cache_mock.save_active_token.assert_called_once()
    user_service_mock.create_user.assert_called_once()
