from loguru import logger
from typing import Any, Dict, Tuple, Optional
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, HTTPException
from fastapi.security import SecurityScopes
from dependency_injector.wiring import inject, Provide
from socketio.asyncio_namespace import AsyncNamespace
from socketio.exceptions import ConnectionRefusedError

# Application
from app import services, security
from app.schemas import UserSchema
from app.containers import Application

ws_router = APIRouter()


@ws_router.websocket("/ws/task_info/{room_id}")
@inject
async def websocket_task_info_endpoint(
    websocket: WebSocket,
    room_id: str,
    task_websocket_manager: services.TaskWebsocketManager = Depends(
        Provide[Application.services.task_websocket_manager]
    ),
    task_socketio_manager: services.TaskSocketioManager = Depends(
        Provide[Application.services.task_socketio_manager]
    ),
):
    await task_websocket_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Receive data: {data}")
            await task_socketio_manager.emit_task_info(payload=data, room_id=room_id)
            await websocket.send_text("ok")

    except WebSocketDisconnect:
        await task_websocket_manager.disconnect(websocket)


@ws_router.websocket("/ws/task_status/{task_id}")
@inject
async def websocket_task_status_endpoint(
    websocket: WebSocket,
    task_id: str,
    current_user: UserSchema.UserWithRoles = Depends(
        security.websocket_get_current_user
    ),
    task_websocket_manager: services.TaskWebsocketManager = Depends(
        Provide[Application.services.task_websocket_manager]
    ),
):
    if current_user:
        logger.info(f"User connect: {current_user}")
        await task_websocket_manager.connect(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                logger.info(f"Receive data: {data}")
                await task_websocket_manager.update_task_status(
                    websocket, task_id=task_id
                )
                await websocket.send_text("ok")

        except WebSocketDisconnect:
            await task_websocket_manager.disconnect(websocket)


###############################################################################
#                   SocketIO Namespace
###############################################################################


class TaskSocketIONamespace(AsyncNamespace):
    async def on_connect(
        self,
        sid: str,
        environ: Any,
        auth: Optional[Dict],
    ) -> None:
        logger.info("[TaskNamespace]:: --- Connect --- ")
        current_user = await self._authenticate(sid, auth)
        logger.info(f"User ID: {current_user.id}")

    async def on_join_task_info_room(self, sid: str, payload: Dict) -> Tuple[str, int]:
        logger.info(f"[TaskNamespace]::Join task info room: {payload}")
        self.enter_room(sid, payload["room_id"])
        return "ok", 200

    async def on_leave_task_info_room(self, sid: str, payload: Dict) -> Tuple[str, int]:
        logger.info(f"[TaskNamespace]::Leave task info room: {payload}")
        self.leave_room(sid, payload["room_id"])
        return "ok", 200

    async def on_join_task_status_room(
        self, sid: str, payload: Dict
    ) -> Tuple[str, int]:
        logger.info(f"[TaskNamespace]::Join task status room: {payload}")
        self.enter_room(sid, payload["room_id"])
        return "ok", 200

    async def on_leave_task_status_room(
        self, sid: str, payload: Dict
    ) -> Tuple[str, int]:
        logger.info(f"[TaskNamespace]::Leave task status room: {payload}")
        self.leave_room(sid, payload["room_id"])
        return "ok", 200

    async def on_disconnect(self, sid: str) -> None:
        logger.info("[TaskNamespace]:: --- Disconnect ---")

    async def _authenticate(
        self,
        sid: str,
        auth: Optional[Dict],
        authenticate_service: services.AuthenticationService = Depends(
            Provide[Application.services.authentication_service]
        ),
    ) -> UserSchema.UserWithRoles:
        if not auth:
            logger.warning(
                "[TaskNamespace]::Authenticate error: without authentication"
            )
            await self.disconnect(sid)
            raise ConnectionRefusedError

        if (token := auth.get("token")) is None:
            logger.warning(
                "[TaskNamespace]::Authenticate error: without authentication token"
            )
            await self.disconnect(sid)
            raise ConnectionRefusedError

        try:
            current_user = await authenticate_service.authenticate_jwt(
                SecurityScopes(), token=token
            )
        except HTTPException as e:
            logger.info(f"[TaskNamespace]::Authenticate error: {e}")
            await self.disconnect(sid)
            raise ConnectionRefusedError

        return current_user
