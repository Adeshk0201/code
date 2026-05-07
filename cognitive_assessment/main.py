from fastapi import FastAPI, WebSocket
from api.routes import router
from api.websocket_handler import assessment_ws_endpoint

app = FastAPI(title="Cognitive Assessment System", version="1.0.0")

app.include_router(router, prefix="/api")


@app.websocket("/ws/assessment")
async def ws_assessment(websocket: WebSocket):
    await assessment_ws_endpoint(websocket)