from fastapi import WebSocket, WebSocketDisconnect
from core.controller import AssessmentController
from models.schemas import PatientInfo, CaretakerTruth
from utils.logger import get_logger
import json

logger = get_logger(__name__)

controller = AssessmentController()


async def assessment_ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    session_id = None

    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            msg_type = message.get("type")
            payload = message.get("payload", {})

            if msg_type == "start":
                patient = PatientInfo(**payload["patient"])
                caretaker = CaretakerTruth(**payload["caretaker"])
                ctx = controller.create_session(patient, caretaker)
                session_id = ctx.session_id
                response = controller.start(session_id)
                await websocket.send_json(response)

            elif msg_type == "answer":
                if not session_id:
                    await websocket.send_json({"error": "No active session"})
                    continue
                answer = payload.get("answer", "")
                response = controller.step(session_id, answer)
                await websocket.send_json(response)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({"error": f"Unknown message type: {msg_type}"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected | session={session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})