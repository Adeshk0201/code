from fastapi import FastAPI, WebSocket
from app.websocket.ws_manager import websocket_endpoint

app = FastAPI()

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket_endpoint(websocket)