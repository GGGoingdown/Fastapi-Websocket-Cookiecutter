import time
from typing import Dict, Any
from loguru import logger
from celery import shared_task
from celery.signals import task_postrun
from dependency_injector.wiring import inject, Provide
from asgiref.sync import async_to_sync

# application
from app import utils, services
from app.broker import broker_utils
from app.containers import Application


@shared_task()
def health_check() -> Dict:
    return {"detail": "health"}


@shared_task()
def long_trip_event(sleep_t: int = 10) -> None:
    logger.info(f"[LongTripEvent]::Execute task time: {utils.get_utc_now()}")
    time.sleep(sleep_t)
    logger.info(f"[LongTripEvent]::Finished task time{utils.get_utc_now()}")


@task_postrun.connect(sender=long_trip_event)
@inject
def long_trip_event_postrun(
    task_id: str,
    task_ws_manager: services.TaskWsManager = Provide[
        Application.services.task_ws_manager
    ],
    **kwargs: Any,
):
    task_state = broker_utils.get_task_info(task_id)
    logger.info(f"[LongTripEvent]::{task_id} -> {task_state}")
    async_to_sync(task_ws_manager.updata_task_state)(task_id, task_state)
