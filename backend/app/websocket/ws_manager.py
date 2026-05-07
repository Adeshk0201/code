from fastapi import WebSocket
from app.core.assessment_loop import controller

async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    response = await controller.run()

    await websocket.send_json(response)

    while True:

        data = await websocket.receive_json()

        answer = data.get("answer")

        question = data.get("question")

        await controller.process_answer(question, answer)

        response = await controller.run()

        await websocket.send_json(response)

        if controller.context.state.stop:
            break

    await websocket.close()