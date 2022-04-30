from functools import lru_cache
from enum import Enum
from typing import Optional, List
from pydantic import BaseSettings, Field, AnyUrl

# Log level
class LogLevel(str, Enum):
    DEUBG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Environment Mode
class EnvironmentMode(str, Enum):
    TEST = "TEST"
    DEV = "DEV"
    PROD = "PROD"


# JWT
class JWT(BaseSettings):
    secret_key: str = Field(env="JWT_SECRET_KEY")
    algorithm: str = Field(env="JWT_ALGORITHM")
    expire_min: int = Field(120, env="JWT_EXPIRE_TIME_MINUTE")


# Application
class Application(BaseSettings):
    env_mode: EnvironmentMode = Field(EnvironmentMode.DEV, env="ENVIRONMENT")

    cors_allowed_origins: List[str] = [
        "http://localhost",
        "https://localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


# Sentry
class SentryConfiguration(BaseSettings):
    dns: Optional[AnyUrl] = Field(env="SENTRY_DNS")
    trace_sample_rates: Optional[float] = Field(1.0, env="SENTRY_TRACE_SAMPLE_RATE")


# Redis
class RedisConfiguration(BaseSettings):
    host: str = Field(env="REDIS_HOST")
    port: str = Field(env="REDIS_PORT")
    username: str = Field(env="REDIS_USERNAME")
    password: str = Field(env="REDIS_PASSWORD")
    backend_db: int = Field(0, env="REDIS_BACKEND_DB")
    result_db: int = Field(1, en="REDIS_RESULT_DB")


# Redis Broadcaster
class BroadcasterConfiguration(BaseSettings):
    host: str = Field(env="BROADCASTER_HOST")
    port: str = Field(env="BROADCASTER_PORT")


# Postgres
class PostgresConfiguration(BaseSettings):
    host: str = Field(env="POSTGRES_HOST")
    port: str = Field(env="POSTGRES_PORT")
    username: str = Field(env="POSTGRES_USERNAME")
    password: str = Field(env="POSTGRES_PASSWORD")
    db: str = Field(env="POSTGRES_DB")


# RabbitMQ
class RabbitMQConfiguration(BaseSettings):
    host: str = Field(env="RABBITMQ_HOST")
    port: str = Field(env="RABBITMQ_PORT")
    username: str = Field(env="RABBITMQ_USERNAME")
    password: str = Field(env="RABBITMQ_PASSWORD")


class Settings(BaseSettings):
    app: Application = Application()
    # JWT
    jwt: JWT = JWT()

    # Sentry Monitor
    sentry: SentryConfiguration = SentryConfiguration()

    # RDBMS
    pg: PostgresConfiguration = PostgresConfiguration()

    # Redis
    redis: RedisConfiguration = RedisConfiguration()

    # Redis Broadcaster
    broadcaster: BroadcasterConfiguration = BroadcasterConfiguration()

    # RabbitMQ
    rabbitmq: RabbitMQConfiguration = RabbitMQConfiguration()


@lru_cache(maxsize=50)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
