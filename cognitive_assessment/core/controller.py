import uuid
from core.context import Context
from core.stopping_conditions import StoppingConditions
from core.section_manager import SectionManager
from models.schemas import PatientInfo, CaretakerTruth
from utils.logger import get_logger

logger = get_logger(__name__)


class AssessmentController:
    """
    Central orchestrator. Controls the assessment loop.
    Agents will be plugged in here in next phase.
    """

    def __init__(self):
        self.section_manager = SectionManager()
        self.stopping = StoppingConditions()
        self.sessions: dict[str, Context] = {}

    def create_session(self, patient: PatientInfo, caretaker: CaretakerTruth) -> Context:
        session_id = str(uuid.uuid4())
        ctx = Context(
            session_id=session_id,
            patient=patient,
            caretaker=caretaker,
        )
        self.sessions[session_id] = ctx
        logger.info(f"Session created: {session_id} | Patient: {patient.name}")
        return ctx

    def get_session(self, session_id: str) -> Context | None:
        return self.sessions.get(session_id)

    def generate_question(self, ctx: Context) -> str:
        """
        STUB: In next phase, this calls QuestionAgent(LLM).
        For now returns deterministic placeholder.
        """
        section = ctx.current_section
        count = ctx.active_section.question_count
        hint = self.section_manager.get_section_prompt_hint(section)

        # Placeholder questions per section
        placeholders = {
            "orientation": [
                "What is today's date?",
                "What day of the week is it?",
                "What city are we currently in?",
                "What season is it right now?",
                "Can you tell me the name of this place?",
            ],
            "memory": [
                "I will say 3 words: Apple, Table, Penny. Please remember them.",
                "Can you repeat those 3 words back to me?",
                "What did you have for breakfast today?",
                "What is the name of the current Prime Minister of India?",
                "Earlier I mentioned 3 words — can you recall them?",
            ],
            "reasoning": [
                "If you have 10 rupees and spend 3, how many do you have?",
                "What do a train and a bus have in common?",
                "Count backwards from 20 to 1.",
                "What would you do if you found a stamped envelope on the street?",
                "Spell the word 'WORLD' backwards.",
            ],
        }

        questions = placeholders.get(section, ["Tell me how you are feeling today."])
        q = questions[count % len(questions)]
        ctx.current_question = q
        return q

    def process_answer(self, ctx: Context, answer: str) -> dict:
        """
        STUB: In next phase, calls ConfidenceAgent + ScoringAgent.
        For now uses dummy scoring.
        """
        # Dummy: score 1.0 if answer is non-empty and long enough
        score = 1.0 if len(answer.strip()) > 3 else 0.3
        confidence = min(0.5 + (ctx.active_section.question_count * 0.15), 1.0)

        ctx.update_after_answer(answer=answer, score=score, confidence=confidence)
        logger.info(
            f"[{ctx.session_id}] Section={ctx.current_section} | "
            f"Q#{ctx.active_section.question_count} | Score={score} | Conf={confidence:.2f}"
        )
        return {"score": score, "confidence": confidence}

    def step(self, session_id: str, answer: str) -> dict:
        """
        Main assessment loop step.
        Called after every user answer.
        Returns next question OR completion status.
        """
        ctx = self.get_session(session_id)
        if not ctx:
            return {"error": "Session not found"}

        if ctx.assessment_complete:
            return self._completion_response(ctx)

        # 1. Process answer
        self.process_answer(ctx, answer)

        # 2. Check stopping
        stop, reason = self.stopping.should_stop_section(ctx.active_section)

        if stop:
            logger.info(f"[{ctx.session_id}] Section '{ctx.current_section}' stopping: {reason}")
            moved = self.section_manager.transition_section(ctx, reason)

            if not moved:
                # Assessment complete
                return self._completion_response(ctx)

        # 3. Generate next question
        next_q = self.generate_question(ctx)

        return {
            "type": "question",
            "session_id": session_id,
            "section": ctx.current_section,
            "question": next_q,
            "question_number": ctx.active_section.question_count + 1,
            "context_snapshot": ctx.get_context_snapshot(),
        }

    def start(self, session_id: str) -> dict:
        """Called once to begin the assessment."""
        ctx = self.get_session(session_id)
        if not ctx:
            return {"error": "Session not found"}

        first_q = self.generate_question(ctx)
        return {
            "type": "question",
            "session_id": session_id,
            "section": ctx.current_section,
            "question": first_q,
            "question_number": 1,
            "context_snapshot": ctx.get_context_snapshot(),
        }

    def _completion_response(self, ctx: Context) -> dict:
        return {
            "type": "complete",
            "session_id": ctx.session_id,
            "stop_reason": ctx.stop_reason,
            "scores": ctx.get_full_scores(),
            "total_questions": len(ctx.global_history),
        }