import sentry_sdk
import celery
from typing import Any, Dict
from loguru import logger
from sentry_sdk.integrations.celery import CeleryIntegration
from celery import current_app as current_celery_app
from celery.result import AsyncResult
from celery.signals import worker_process_init
from kombu import Queue

# Application
from app.config import settings

# Inititalize
@worker_process_init.connect
def worker_initialize(*args: Any, **kwargs: Any) -> None:
    logger.info("Worker initialize ...")
    sentry_sdk.init(dsn=settings.sentry.dns, integrations=[CeleryIntegration()])


def get_task_info(task_id) -> Dict:
    """
    return task info according to the task_id
    """
    task = AsyncResult(task_id)
    if task.state == "FAILURE":
        error = str(task.result)
        response = {
            "state": task.state,
            "error": error,
        }
    else:
        response = {
            "state": task.state,
        }
    return response


# Configuration
class CeleryConfiguration:
    broker_url = f"amqp://{settings.rabbitmq.username}:{settings.rabbitmq.password}@{settings.rabbitmq.host}:{settings.rabbitmq.port}//"

    result_backend = f"redis://{settings.redis.username}:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}/{settings.redis.result_db}"

    task_serializer = "pickle"
    result_serializer = "pickle"
    event_serializer = "json"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_accept_content = ["application/json", "application/x-python-serialize"]
    result_expires = 1800

    task_queues = (Queue("p1"), Queue("p2"))
    task_default_queue = "p1"
    task_default_exchange = "Task"
    task_default_exchange_type = "direct"


def create_celery() -> celery:
    celery_app = current_celery_app
    celery_app.config_from_object(CeleryConfiguration)

    return celery_app
