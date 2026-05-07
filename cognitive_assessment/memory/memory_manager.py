from memory.stm import ShortTermMemory
from memory.vector_store import VectorStore
from memory.ltm import LongTermMemory
from llm.openai_provider import get_llm
from utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """
    Unified memory interface.
    STM  → sliding window of recent interactions
    FAISS → semantic retrieval
    LTM  → PostgreSQL persistence
    """

    def __init__(self, db_session):
        self.stm = ShortTermMemory()
        self.vector = VectorStore()
        self.ltm = LongTermMemory(db_session)
        self._llm = get_llm()

    async def record_interaction(
        self,
        session_id: str,
        section: str,
        question: str,
        answer: str,
        score: float,
        confidence: float,
    ):
        # STM
        self.stm.add(section, question, answer, score, confidence)
        # FAISS
        self.vector.add_interaction(section, question, answer, session_id)
        # LTM
        await self.ltm.save_interaction(session_id, section, question, answer, score, confidence)

    async def retrieve_semantic(self, query: str) -> str:
        return self.vector.retrieve_relevant(query)

    def get_stm_prompt(self) -> str:
        return self.stm.format_for_prompt()

    async def summarize_stm(self) -> str:
        """Compress STM window into a short summary using LLM."""
        recent = self.stm.format_for_prompt()
        if recent == "No recent interactions.":
            return recent

        system = """You are a clinical memory summarizer.
Compress the following patient interactions into 2-3 sentences.
Focus on cognitive indicators: memory gaps, confusion, correct answers.
Be concise and clinical."""

        summary = await self._llm.complete(system, recent, json_mode=False)
        logger.info("STM summarized.")
        return summary.strip()

    async def build_memory_context(self, current_question: str) -> dict:
        """Returns memory dict to be injected into context snapshot."""
        stm_text = self.stm.format_for_prompt()
        semantic_hits = await self.retrieve_semantic(current_question)
        summary = await self.summarize_stm()
        return {
            "stm_recent": stm_text,
            "semantic_relevant": semantic_hits,
            "memory_summary": summary,
        }

    async def persist_session_start(self, session_id: str, patient, caretaker: dict):
        await self.ltm.save_patient(
            patient_id=patient.patient_id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
        )
        await self.ltm.save_session(session_id, patient.patient_id, caretaker)

    async def persist_section_complete(self, session_id: str, section: str,
                                        score: float, confidence: float,
                                        question_count: int, observations: str):
        await self.ltm.save_section_score(
            session_id, section, score, confidence, question_count, observations
        )

    async def persist_report(self, session_id: str, report: dict, consistency: dict):
        await self.ltm.save_report(
            session_id=session_id,
            report_text=report.get("report", ""),
            risk_level=report.get("risk_level", "unknown"),
            recommendations=report.get("recommendations", []),
            consistency_score=consistency.get("consistency_score", 1.0),
            consistency_mismatches=consistency.get("mismatches", []),
        )
        # Store summary in FAISS too
        self.vector.add_summary(report.get("report", ""), session_id)