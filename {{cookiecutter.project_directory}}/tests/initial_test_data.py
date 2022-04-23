from tortoise import run_async
from tenacity import retry, stop_after_attempt, wait_fixed
from loguru import logger
from typing import Dict, Iterable

# Application
from app.containers import Application
from app.models import User, Role
from app.services import BaseAuthService
from app.constants import RoleEnum

# Tests
from tests import test_utils


max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


def create_user_info(fake_user: test_utils.FakeUser) -> Dict:
    user_info = fake_user.dict(exclude={"password"})
    password_hash = BaseAuthService.get_password_hash(fake_user.password)
    user_info.update({"password_hash": password_hash})
    return user_info


async def create_roles() -> None:
    for role in RoleEnum:
        role_name = role.value
        logger.info(f"--- Create role: {role_name} ---")
        await Role.create(name=role_name)


async def get_role_by_name(name: str) -> Role:
    if role := await Role.filter(name=name).first():
        return role
    raise ValueError(f"Can not get role: {name}")


async def create_user(payload: Dict, roles: Iterable[RoleEnum]):
    if user := await User.filter(email=payload["email"]).first():
        logger.info("--- Already create user ---")
    else:
        logger.info("--- Create user ---")
        user = User(**payload)
        await user.save()

        for role in roles:
            role_model = await get_role_by_name(role.value)
            await user.roles.add(role_model)

        await User.get(id=user.id)
        logger.info("--- Create user successful ---")


@retry(stop=stop_after_attempt(max_tries), wait=wait_fixed(wait_seconds))
async def connect(container: Application):
    try:
        await container.gateways.db_resource.init()

    except Exception as e:
        logger.error(e)
        raise e


async def main():
    container = Application()
    try:
        logger.info("--- Connect DB ---")
        await connect(container)
        # Create roles
        await create_roles()
        # Create fake users
        users = test_utils.FAKE_USERS
        for user, func in users.items():
            logger.info(f"--- User: {user} ---")
            fake_user = func()
            user_info = create_user_info(fake_user)
            await create_user(user_info, fake_user.role)

    finally:
        await container.gateways.db_resource.shutdown()


if __name__ == "__main__":
    run_async(main())
