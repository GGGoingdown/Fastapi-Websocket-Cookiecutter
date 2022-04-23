from typing import Callable, Dict, Any, List

# Application
from app.main import app
from app import models
from app.schemas import UserSchema
from app.constants import RoleEnum


# Dependency override
async def override_get_current_user_in_cache_user_admin():
    user = await models.User.get(name="admin")
    return UserSchema.UserWithRoles(
        id=user.id,
        roles=[RoleEnum.ADMIN.value],
    )


async def override_get_current_user_in_cache_user_super():
    user = await models.User.get(name="super")
    return UserSchema.UserWithRoles(
        id=user.id,
        roles=[RoleEnum.SUPER_ADMIN.value],
    )


# Fake headers generator
def create_headers(role: RoleEnum) -> Dict:
    authorization_service = app.container.services.authorization_service()
    token = authorization_service.create_jwt_token(user_id=1, scopes=[role.value])
    headers = {"Authorization": f"Bearer {token}"}
    return headers


#####################################################################################
#                           Fake Users
#####################################################################################
class FakeUser(UserSchema.UserInfo):
    password: str
    role: List[RoleEnum]


def _create_user(**kwargs: Any) -> FakeUser:
    return FakeUser(**kwargs)


def fake_super_user() -> FakeUser:
    user_info = {
        "name": "super",
        "email": "super@gmail.com",
        "is_active": True,
        "is_admin": True,
        "password": "super",
        "role": [RoleEnum.SUPER_ADMIN],
    }
    return _create_user(**user_info)


def fake_admin_user() -> FakeUser:
    user_info = {
        "name": "admin",
        "email": "admin@gmail.com",
        "is_active": True,
        "is_admin": True,
        "password": "admin",
        "role": [RoleEnum.ADMIN],
    }
    return _create_user(**user_info)


def fake_guest_user() -> FakeUser:
    user_info = {
        "name": "guest",
        "email": "guest@gmail.com",
        "is_active": True,
        "is_admin": False,
        "password": "guest",
        "role": [RoleEnum.GUEST],
    }
    return _create_user(**user_info)


async def mock_user_in_db(name: str = "super") -> UserSchema.UserInDB:
    user = await models.User.get(name=name)
    return UserSchema.UserInDB.from_orm(user)


async def mock_user_model(name: str = "guest") -> models.User:
    return await models.User.get(name=name)


FAKE_USERS: Dict[str, Callable] = {
    "SUPER": fake_super_user,
    "ADMIN": fake_admin_user,
    "GUEST": fake_guest_user,
}
