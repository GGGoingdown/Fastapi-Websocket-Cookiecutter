from typing import Iterable, Optional
from loguru import logger
from tortoise.exceptions import IntegrityError

# Application
from app import repositories, exceptions
from app.models import User, Role
from app.schemas import UserSchema
from app.constants import RoleEnum


class UserRoleService:
    __slots__ = ("_user_role_repo",)

    def __init__(self, user_role_repo: repositories.UserRoleRepo) -> None:
        self._user_role_repo = user_role_repo

    async def get_roles_by_user_id(self, user_id: int) -> Iterable[str]:
        roles = await self._user_role_repo.get_by_user_id(user_id)
        return [role.value for role in roles]

    async def get_role_by_name(self, role_name: RoleEnum) -> Role:
        if role := await self._user_role_repo.get_by_name(role_name.value):
            return role
        raise exceptions.RoleNotFoundError()


class UserService:
    __slots__ = ("_user_repo", "_user_role_repo", "_user_cache")

    def __init__(
        self,
        user_repo: repositories.UserRepo,
        user_role_repo: repositories.UserRoleRepo,
        user_cache: repositories.UserCache,
    ) -> None:
        self._user_repo = user_repo
        self._user_role_repo = user_role_repo
        self._user_cache = user_cache

    async def create_user(
        self,
        user_payload: UserSchema.UserCreate,
        password_hash: str,
        *,
        role_model: Role,
    ) -> User:
        payload = user_payload.dict(exclude={"password", "verify_password"})
        try:
            user_model = await self._user_repo.create(
                **payload, password_hash=password_hash, is_active=False, is_admin=False
            )

            await self._user_repo.add_roles(user_model, [role_model])

        except IntegrityError as e:  # Tortoise Integrity exceptions
            logger.warning(e)
            raise exceptions.SaveDBUserError(user_payload.email)

        return user_model

    async def add_user_role(self, user_model: User, role_model: Iterable[Role]) -> None:
        await self._user_repo.add_roles(user_model, role_model)

    async def activate_user(self, user_id: int) -> None:
        res = await self._user_repo.update_by_id(user_id, is_active=True)
        if not res:
            raise exceptions.UserUpdateError(user_id)

    async def get_all_users(
        self, *, offset: int = 0, limit: int = 100
    ) -> Iterable[User]:
        users = await self._user_repo.get_all(offset=offset, limit=limit)
        return users

    async def get_user_with_roles(
        self, user_id: int
    ) -> Optional[UserSchema.UserInfoRoles]:
        user = await self._user_repo.get_by_id_with_role(id=user_id)
        return UserSchema.UserInfoRoles.from_orm(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        user = await self._user_repo.get_by_mail(email=email)
        return user if user else None

    async def save_user_in_cache(self, user_id: int) -> bool:
        if res := await self._user_cache.save(user_id):
            return res
        raise exceptions.CacheUserError(res)

    async def user_exists_in_cache(self, user_id: int) -> bool:
        res = await self._user_cache.get(user_id)
        return True if res else False

    async def remove_user_in_cache(self, user_id: int) -> bool:
        res = await self._user_cache.delete(user_id)
        return True if res else False
