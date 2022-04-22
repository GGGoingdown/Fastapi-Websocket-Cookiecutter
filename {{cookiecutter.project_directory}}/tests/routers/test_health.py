import pytest

ENDPOINT = "/health"


@pytest.mark.health
@pytest.mark.asyncio
async def test_health_check(client):
    res = await client.get(ENDPOINT)
    assert res.status_code == 200, f"Invalid status code: {res.status_code}"

    assert res.json() == {"detail": "health"}
