import json
import logging
import uvicorn
import aioredis
from jinja2 import Template
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from websockets.exceptions import ConnectionClosed
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.websockets import (
    WebSocket,
    WebSocketDisconnect
)


logging.basicConfig(level=logging.INFO)


WEB_PORT = 8080
# REDIS_ADDRESS = 'redis://127.0.0.1:6379'
REDIS_ADDRESS = 'redis://redis:6379'


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


html_template = Template("""
<!DOCTYPE html>
<html>
    <head>
        <title>logs</title>
    </head>
    <body>
        <ul id='messages'>
        <script>
            var ws = new WebSocket('ws://0.0.0.0:{{ port }}/ws/{{ application }}');
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
""")


@app.get("/web/ws/{application}")
async def ws_view(application: str):
    html = html_template.render(port=WEB_PORT, application=application)
    return HTMLResponse(html)


@app.get("/sse/{application}")
async def sse(application: str):
    async def stream(redis_subscriber):
        async for message in redis_subscriber[0].iter():
            if not message:
                continue
            message_log_json = json.dumps(json.loads(message)) + '\n'
            logging.info(f"{ws}: {message_log_json}")
            yield message_log_json.encode(encoding='utf-8')

    channel_name = f'{application}.realtime-log-web-viewer_default'

    redis = await aioredis.create_redis(REDIS_ADDRESS)
    redis_subscriber = await redis.subscribe(channel_name)

    return StreamingResponse(stream(redis_subscriber))


@app.websocket("/ws/{application}")
async def ws(ws: WebSocket, application: str):
    await ws.accept()

    # my_application_fakelog_a_realtime-log-web-viewer_default
    channel_name = f'{application}.realtime-log-web-viewer_default'

    redis = await aioredis.create_redis(REDIS_ADDRESS)
    redis_subscriber = await redis.subscribe(channel_name)

    while True:
        try:
            async for message in redis_subscriber[0].iter():
                if not message:
                    continue
                try:
                    message_log_json = json.loads(message)
                    logging.info(f"{ws}: {message_log_json}")
                    await ws.send_json(message_log_json)
                except (ConnectionClosed, WebSocketDisconnect):
                    logging.info(f"{ws}: disconnected from channel {channel_name}")
                    return
        except Exception as e:
            logging.error(f"read timed out for stream {channel_name}, {e}")
            return


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=WEB_PORT
    )


if __name__ == "__main__":
    main()
