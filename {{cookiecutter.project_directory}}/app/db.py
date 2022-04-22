from this import d
import aioredis
from typing import Dict, Any
from loguru import logger
from tortoise import Tortoise, connections
from dependency_injector import resources
from broadcaster import Broadcast

# from tortoise.contrib.fastapi import register_tortoise

# Configuration
from app.config import settings

db_model_list = ["app.models"]


def get_redis_url() -> str:
    url = f"redis://{settings.redis.username}:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}/{settings.redis.backend_db}"
    return url


def get_redis_broadcaster_url() -> str:
    url = f"redis://{settings.broadcaster.host}:{settings.broadcaster.port}/"
    return url


def get_pg_url() -> str:
    url = f"postgres://{settings.pg.username}:{settings.pg.password}@{settings.pg.host}:{settings.pg.port}/{settings.pg.db}"
    return url


def get_tortoise_config(db_url: str = None) -> Dict:
    config = {
        "connections": {"default": db_url if db_url else get_pg_url()},
        "apps": {
            "models": {
                "models": [*db_model_list, "aerich.models"],
                "default_connection": "default",
            },
        },
    }
    return config


# Tortoise ORM Configuration
TORTOISE_ORM = get_tortoise_config()


def redis_init() -> aioredis:
    connect_uri = get_redis_url()
    redis_client = aioredis.from_url(
        connect_uri,
        encoding="utf-8",
        decode_responses=True,
    )
    return redis_client


def broadcaster_init() -> Broadcast:
    url = get_redis_broadcaster_url()
    broadcast = Broadcast(url)
    return broadcast


class DBResource(resources.AsyncResource):
    async def init(self, config: Dict = TORTOISE_ORM) -> None:
        logger.info("--- Initialize DB resource ---")
        await Tortoise.init(config=config)

    async def shutdown(self, *args: Any, **kwargs: Any):
        logger.info("--- Shutdown DB resource ---")
        await connections.close_all()


class BroadcasterResource(resources.AsyncResource):
    async def init(self, broadcaster: Broadcast):
        logger.info("--- Initialize Broadcaster resource ---")
        self.broadcaster = broadcaster
        await self.broadcaster.connect()

    async def shutdown(self, *args, **kwargs):
        logger.info("--- Shutdown Broadcaster resource ---")
        await self.broadcaster.disconnect()
