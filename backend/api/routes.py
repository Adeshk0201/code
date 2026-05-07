from fastapi import APIRouter
from core.controller import AssessmentController

router = APIRouter()
controller = AssessmentController()


@router.get("/health")
def health():
    return {"status": "ok", "service": "Cognitive Assessment Backend"}


@router.get("/sessions/{session_id}/scores")
def get_scores(session_id: str):
    ctx = controller.get_session(session_id)
    if not ctx:
        return {"error": "Session not found"}
    return ctx.get_full_scores()


@router.get("/sessions/{session_id}/context")
def get_context(session_id: str):
    ctx = controller.get_session(session_id)
    if not ctx:
        return {"error": "Session not found"}
    return ctx.get_context_snapshot()