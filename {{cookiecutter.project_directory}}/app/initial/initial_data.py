import os
from tortoise import run_async
from tenacity import retry, stop_after_attempt, wait_fixed
from loguru import logger
from typing import Dict, Iterable

# Application
from app.containers import Application
from app.models import User, Role
from app.services import BaseAuthService
from app.constants import RoleEnum


max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


def get_super_admin() -> Dict:
    name = os.environ.get("super_admin", "admin")
    mail = os.environ.get("super_admin_email", "admin@gmail.com")
    password = os.environ.get("super_admin_password", "admin")

    return {
        "name": name,
        "email": mail,
        "password_hash": BaseAuthService.get_password_hash(password),
        "is_active": True,
        "is_admin": True,
    }


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
        # Get super admin information
        super_user_info = get_super_admin()
        # Create super admin user
        await create_user(super_user_info, [RoleEnum.SUPER_ADMIN, RoleEnum.ADMIN])

    finally:
        await container.gateways.db_resource.shutdown()


if __name__ == "__main__":
    run_async(main())
