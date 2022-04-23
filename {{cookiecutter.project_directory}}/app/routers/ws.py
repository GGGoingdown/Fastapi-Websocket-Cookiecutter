from loguru import logger
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from dependency_injector.wiring import inject, Provide

# Application
from app import services
from app.containers import Application


ws_router = APIRouter()


@ws_router.websocket("/ws/task_status/{task_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: str,
    task_ws_manager: services.TaskWsManager = Depends(
        Provide[Application.services.task_ws_manager]
    ),
):
    await task_ws_manager.connect(websocket)
    try:
        await task_ws_manager.sender(websocket, task_id=task_id)
    except WebSocketDisconnect:
        logger.info(f"[WS]::Disconnect")
