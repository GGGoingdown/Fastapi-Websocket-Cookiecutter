import aioredis
from loguru import logger
from typing import Tuple

# Application
from app.utils import get_shortuuid


class AuthCache:
    __slots__ = ("_redis_client", "_active_token_expired_sceonds")

    def __init__(
        self, redis_client: aioredis, active_token_expried_min: int = 30
    ) -> None:
        self._redis_client = redis_client
        self._active_token_expired_sceonds = active_token_expried_min * 60

    def _inactive_token_key(self, token: str) -> str:
        return f"inactive:{token}"

    async def save_active_token(self, user_id: int) -> Tuple[bool, str]:
        token = get_shortuuid()
        token_key = self._inactive_token_key(token)
        res = await self._redis_client.setex(
            token_key, self._active_token_expired_sceonds, user_id
        )
        logger.debug(f"[AuthCache]::Save: {res}")
        return res, token

    async def get_active_token(self, token: str) -> int:
        token_key = self._inactive_token_key(token)
        res = await self._redis_client.get(token_key)
        logger.debug(f"[AuthCache]::Get user ID: {res}")
        return res

    async def delete_active_token(self, token: str) -> int:
        token_key = self._inactive_token_key(token)
        res = await self._redis_client.delete(token_key)
        logger.debug(f"[AuthCache]::Delete: {res}")
        return res
