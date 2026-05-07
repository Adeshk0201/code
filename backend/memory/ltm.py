from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Patient, Session as DBSession, SectionScore, Interaction, Report
from utils.logger import get_logger

logger = get_logger(__name__)


class LongTermMemory:
    """Handles all PostgreSQL persistence for sessions, scores, interactions, reports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_patient(self, patient_id: str, name: str, age: int, gender: str):
        existing = await self.db.get(Patient, patient_id)
        if not existing:
            patient = Patient(id=patient_id, name=name, age=age, gender=gender)
            self.db.add(patient)
            await self.db.commit()

    async def save_session(self, session_id: str, patient_id: str, caretaker_info: dict):
        session = DBSession(
            id=session_id,
            patient_id=patient_id,
            caretaker_info=caretaker_info,
        )
        self.db.add(session)
        await self.db.commit()

    async def save_interaction(self, session_id: str, section: str, question: str,
                                answer: str, score: float, confidence: float):
        interaction = Interaction(
            session_id=session_id,
            section=section,
            question=question,
            answer=answer,
            score=score,
            confidence=confidence,
        )
        self.db.add(interaction)
        await self.db.commit()

    async def save_section_score(self, session_id: str, section: str,
                                  score: float, confidence: float,
                                  question_count: int, observations: str = ""):
        ss = SectionScore(
            session_id=session_id,
            section_name=section,
            score=score,
            confidence=confidence,
            question_count=question_count,
            observations=observations,
        )
        self.db.add(ss)
        await self.db.commit()

    async def save_report(self, session_id: str, report_text: str, risk_level: str,
                           recommendations: list, consistency_score: float,
                           consistency_mismatches: list):
        report = Report(
            session_id=session_id,
            report_text=report_text,
            risk_level=risk_level,
            recommendations=recommendations,
            consistency_score=consistency_score,
            consistency_mismatches=consistency_mismatches,
        )
        self.db.add(report)
        await self.db.commit()

    async def get_past_sessions(self, patient_id: str) -> list:
        result = await self.db.execute(
            select(DBSession).where(DBSession.patient_id == patient_id)
        )
        return result.scalars().all()

    async def get_past_reports(self, patient_id: str) -> list:
        sessions = await self.get_past_sessions(patient_id)
        session_ids = [s.id for s in sessions]
        if not session_ids:
            return []
        result = await self.db.execute(
            select(Report).where(Report.session_id.in_(session_ids))
        )
        return result.scalars().all()