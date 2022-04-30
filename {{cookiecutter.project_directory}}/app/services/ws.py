from loguru import logger
from typing import Any
from abc import ABCMeta, abstractmethod
from fastapi import WebSocket
from socketio.asyncio_pubsub_manager import AsyncPubSubManager

# Application
from app.broker import get_task_info
from app.constants.socketio_namespaces import NamespaceEnum


class WebsocketManager(metaclass=ABCMeta):
    @abstractmethod
    async def connect(self, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def disconnect(self, websocket: WebSocket) -> None:
        pass


class TaskWebsocketManager(WebsocketManager):
    async def connect(self, websocket: WebSocket) -> None:
        logger.info("[TaskWebsocketManager]::Connect")
        await websocket.accept()

    async def disconnect(self, websocket: WebSocket) -> None:
        logger.info("[TaskWebsocketManager]::Disconnect")

    async def update_task_status(self, websocket: WebSocket, *, task_id: str) -> None:
        task_stauts = get_task_info(task_id)
        logger.info(f"[TaskWebsocketManager]::Update task status: {task_stauts}")
        await websocket.send_json(task_stauts)


class SocketioManager:
    __slots__ = ("socketio_client",)

    namespace: NamespaceEnum

    def __init__(self, socketio_client: AsyncPubSubManager) -> None:
        self.socketio_client = socketio_client

    async def emit(
        self, path: str, *, data: Any, room: str, namespace: NamespaceEnum
    ) -> None:
        await self.socketio_client.emit(
            path, data=data, room=room, namespace=f"/{namespace.value}"
        )


class TaskSocketioManager(SocketioManager):
    namespace = NamespaceEnum.task

    def __init__(self, socketio_client: AsyncPubSubManager) -> None:
        super().__init__(socketio_client)

    async def _emit_namespace(self, path: str, *, data: Any, room: str) -> None:
        await self.emit(path, data=data, room=room, namespace=self.namespace)

    async def emit_task_status(
        self,
        *,
        task_id: str,
        payload: Any,
    ) -> None:
        logger.info(f"[TaskSocketioManager]::Emit task status: {task_id}")
        await self._emit_namespace("task_status", data=payload, room=task_id)

    async def emit_task_info(self, *, payload: Any, room_id: str) -> None:
        await self._emit_namespace("task_info", data=payload, room=room_id)
