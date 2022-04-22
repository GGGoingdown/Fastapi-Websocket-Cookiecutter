import pytest
from httpx import AsyncClient
from unittest import mock

# Application
from app import repositories


ENDPOINT = "/auth/activate-user?t={token}"


@pytest.mark.activate_user
@pytest.mark.asyncio
async def test_activate_user(client: AsyncClient, app):
    auth_cache_mock = mock.AsyncMock(spec=repositories.AuthCache)
    auth_cache_mock.get_active_token.return_value = 1

    with app.container.services.auth_cache.override(auth_cache_mock):
        res = await client.get(ENDPOINT.format(token="some_token"))

    assert res.status_code == 200, f"Error status code: {res.status_code}, Expected 200"

    # Validation
    assert res.json() == {
        "detail": "activate user success"
    }, f"Unexpected response: {res.json()}"

    auth_cache_mock.get_active_token.assert_called_once()


@pytest.mark.activate_user
@pytest.mark.asyncio
async def test_activate_user_404_not_found(client: AsyncClient, app):
    res = await client.get(ENDPOINT.format(token="fake_token"))

    assert res.status_code == 404, f"Error status code: {res.status_code}, Expected 404"

    assert res.json() == {"detail": "Not found"}, f"Unexpected response: {res.json()}"
