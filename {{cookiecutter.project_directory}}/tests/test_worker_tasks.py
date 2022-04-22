import pytest

# Application
from app.main import celery  # noqa: F401
from app.broker import tasks


@pytest.mark.worker
def test_worker_health_check():
    result = tasks.health_check.delay().get()

    assert result == {"detail": "health"}
