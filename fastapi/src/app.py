from fastapi import (
    FastAPI,
    WebSocket
)
import typing
import uvicorn
import redis
import json
import asyncio
from redis.client import PubSub
from fastapi.responses import HTMLResponse

WEB_PORT = 8080

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>logs</title>
    </head>
    <body>
        <ul id='messages'>
        <script>
            var ws = new WebSocket('ws://0.0.0.0:8080/ws');
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
        </script>
    </body>
</html>
"""


# REDIS_ADDRESS = '127.0.0.1'
REDIS_ADDRESS = 'redis'
REDIS_PORT = 6379


class ConnectionManager:
    def __init__(self):
        self.active_connections: typing.List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f'CONECTADO: {len(self.active_connections)}')

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f'DESCONECTADO: {len(self.active_connections)}')

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)


redis_client = redis.Redis(host=REDIS_ADDRESS, port=REDIS_PORT, db=0)
redis_pb = redis_client.pubsub()
redis_pb.subscribe('fakelog')

app = FastAPI()
manager = ConnectionManager()


@app.websocket("/ws")
async def ws_logs(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        for raw_msg in redis_pb.listen():
            if raw_msg['type'] != 'message':
                continue
            log = json.loads(raw_msg['data'].decode('utf-8'))
            print(log)
            await manager.send_message(log, websocket)
            await asyncio.sleep(0)
    except:
        manager.disconnect(websocket)


@app.get("/")
async def get():
    return HTMLResponse(html)


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=WEB_PORT
    )


if __name__ == "__main__":
    main()
