import uuid
from core.context import Context
from core.stopping_conditions import StoppingConditions
from core.section_manager import SectionManager
from models.schemas import PatientInfo, CaretakerTruth
from agents.agent_orchestrator import AgentOrchestrator
from memory.memory_manager import MemoryManager
from utils.logger import get_logger

logger = get_logger(__name__)


class AssessmentController:
    def __init__(self, db_session):
        self.section_manager = SectionManager()
        self.stopping = StoppingConditions()
        self.sessions: dict[str, Context] = {}
        self.memory_managers: dict[str, MemoryManager] = {}
        self.orchestrator = AgentOrchestrator()
        self.db_session = db_session

    def create_session(self, patient: PatientInfo, caretaker: CaretakerTruth) -> Context:
        session_id = str(uuid.uuid4())
        ctx = Context(session_id=session_id, patient=patient, caretaker=caretaker)
        self.sessions[session_id] = ctx
        self.memory_managers[session_id] = MemoryManager(self.db_session)
        logger.info(f"Session created: {session_id}")
        return ctx

    def get_session(self, session_id: str) -> Context | None:
        return self.sessions.get(session_id)

    def _mm(self, session_id: str) -> MemoryManager:
        return self.memory_managers[session_id]

    async def generate_question(self, ctx: Context) -> str:
        # Build memory context
        mem = await self._mm(ctx.session_id).build_memory_context(
            ctx.current_question or ctx.current_section
        )
        ctx.inject_memory(mem)
        snapshot = ctx.get_context_snapshot()
        question = await self.orchestrator.get_question(snapshot)
        ctx.current_question = question
        return question

    async def process_answer(self, ctx: Context, answer: str) -> dict:
        snapshot = ctx.get_context_snapshot()

        conf_result = await self.orchestrator.get_confidence(snapshot, answer)
        confidence = conf_result["confidence"]

        score_result = await self.orchestrator.score_section(
            section=ctx.current_section,
            history=ctx.active_section.history,
            caretaker=ctx.caretaker.model_dump(),
        )
        score = score_result["section_score"]

        ctx.update_after_answer(answer=answer, score=score, confidence=confidence)

        # Record in memory
        await self._mm(ctx.session_id).record_interaction(
            session_id=ctx.session_id,
            section=ctx.current_section,
            question=ctx.current_question,
            answer=answer,
            score=score,
            confidence=confidence,
        )
        return {"score": score, "confidence": confidence}

    async def step(self, session_id: str, answer: str) -> dict:
        ctx = self.get_session(session_id)
        if not ctx:
            return {"error": "Session not found"}
        if ctx.assessment_complete:
            return await self._completion_response(ctx)

        await self.process_answer(ctx, answer)

        stop, reason = self.stopping.should_stop_section(ctx.active_section)
        if stop:
            # Persist section score
            sec = ctx.active_section
            await self._mm(session_id).persist_section_complete(
                session_id=session_id,
                section=ctx.current_section,
                score=sec.score,
                confidence=sec.confidence,
                question_count=sec.question_count,
                observations="",
            )
            moved = self.section_manager.transition_section(ctx, reason)
            if not moved:
                return await self._completion_response(ctx)

        next_q = await self.generate_question(ctx)
        return {
            "type": "question",
            "session_id": session_id,
            "section": ctx.current_section,
            "question": next_q,
            "question_number": ctx.active_section.question_count + 1,
            "context_snapshot": ctx.get_context_snapshot(),
        }

    async def start(self, session_id: str) -> dict:
        ctx = self.get_session(session_id)
        if not ctx:
            return {"error": "Session not found"}
        await self._mm(session_id).persist_session_start(
            session_id, ctx.patient, ctx.caretaker.model_dump()
        )
        first_q = await self.generate_question(ctx)
        return {
            "type": "question",
            "session_id": session_id,
            "section": ctx.current_section,
            "question": first_q,
            "question_number": 1,
            "context_snapshot": ctx.get_context_snapshot(),
        }

    async def _completion_response(self, ctx: Context) -> dict:
        consistency = await self.orchestrator.check_consistency(
            patient_history=ctx.global_history,
            caretaker=ctx.caretaker.model_dump(),
        )
        report = await self.orchestrator.generate_report(
            scores=ctx.get_full_scores(),
            consistency=consistency,
            patient=ctx.patient.model_dump(),
        )
        await self._mm(ctx.session_id).persist_report(ctx.session_id, report, consistency)
        ctx.assessment_complete = True
        return {
            "type": "complete",
            "session_id": ctx.session_id,
            "stop_reason": ctx.stop_reason,
            "scores": ctx.get_full_scores(),
            "consistency": consistency,
            "report": report,
            "total_questions": len(ctx.global_history),
        }