from typing import Dict
from celery.result import AsyncResult


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
