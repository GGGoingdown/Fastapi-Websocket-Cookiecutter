import pytest

# Application
from app import models
from app.constants import RoleEnum

# Tests
from tests import test_utils


@pytest.mark.run(order=1)
@pytest.mark.asyncio
async def test_get_roles_in_db():
    for role in RoleEnum:
        role_model = await models.Role.filter(name=role).first()
        assert role_model.name == role.value, f"Get {role.value} failed"


@pytest.mark.run(order=2)
@pytest.mark.asyncio
async def test_get_users_in_db():
    users = test_utils.FAKE_USERS
    for user, func in users.items():
        fake_user: test_utils.FakeUser = func()
        get_user = await models.User.get(name=fake_user.name)
        assert get_user.email == fake_user.email, f"Get {user} failed"
