from fastapi import APIRouter, Query
from dependency_injector.wiring import inject

# Application
from app.schemas import GenericSchema
from app.broker import task_pipelines

event_router = APIRouter(prefix="/events")


@event_router.post(
    "/long-trip",
    response_model=GenericSchema.TaskResponse,
    responses={201: {"model": GenericSchema.TaskResponse, "description": "Task ID"}},
)
@inject
async def long_trip_event(
    t: int = Query(10, ge=10, le=20),
):
    task_id = task_pipelines.long_trip(t)
    return {"task_id": task_id}
