import asyncio
import datetime
import random
import websockets


room_id = 20
url = f"ws://localhost:8000/ws/task_info/{room_id}"


async def hello():
    async with websockets.connect(url) as websocket:
        while True:
            message = datetime.datetime.utcnow().isoformat() + "Z"
            await websocket.send(message)
            data = await websocket.recv()
            print(f"[{message}]::Send message !! {data}")
            await asyncio.sleep(random.random() * 2 + 1)


if __name__ == "__main__":
    asyncio.run(hello())
