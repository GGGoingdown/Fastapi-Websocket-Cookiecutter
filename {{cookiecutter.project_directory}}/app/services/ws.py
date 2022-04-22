import json
from typing import Any, Dict
from abc import ABCMeta, abstractmethod
from loguru import logger
from broadcaster import Broadcast
from fastapi import WebSocket

# Application
from app.broker import broker_utils


class WebsocketManager(metaclass=ABCMeta):
    def __init__(self, broadcaster: Broadcast) -> None:
        self._broadcaster = broadcaster

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    async def updata_task_state(self, task_id: str, task_state: Dict) -> None:
        await self._broadcaster.connect()
        await self._broadcaster.publish(channel=task_id, message=json.dumps(task_state))
        await self._broadcaster.disconnect()


class TaskWebsocketManager(WebsocketManager):
    def __init__(self, broadcaster: Broadcast) -> None:
        super().__init__(broadcaster)

    async def sender(self, websocket: WebSocket, task_id: str) -> None:
        async with self._broadcaster.subscribe(channel=task_id) as subscriber:
            data = broker_utils.get_task_info(task_id)
            # Send pendind task state
            await websocket.send_json(data)
            async for event in subscriber:
                await websocket.send_json(json.loads(event.message))
