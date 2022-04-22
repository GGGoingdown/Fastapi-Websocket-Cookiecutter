from uuid import UUID
# Application
from app.broker import tasks


def long_trip(sleep_t: int) -> UUID:
    task = tasks.long_trip_event.s(sleep_t).apply_async()
    return task.id
