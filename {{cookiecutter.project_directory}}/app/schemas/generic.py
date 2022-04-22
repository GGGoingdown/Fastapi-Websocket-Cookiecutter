from pydantic import BaseModel


class DetailResponse(BaseModel):
    detail: str


class TaskResponse(BaseModel):
    task_id: str
