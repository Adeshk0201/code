from dataclasses import dataclass, field
from typing import Optional
from models.schemas import PatientInfo, CaretakerTruth


@dataclass
class SectionState:
    name: str
    question_count: int = 0
    score: float = 0.0
    confidence: float = 0.0
    history: list = field(default_factory=list)
    completed: bool = False

    def add_interaction(self, question: str, answer: str, score: float, confidence: float):
        self.history.append({
            "q": question,
            "a": answer,
            "score": score,
            "confidence": confidence
        })
        self.question_count += 1
        # Running average
        n = self.question_count
        self.score = ((self.score * (n - 1)) + score) / n
        self.confidence = ((self.confidence * (n - 1)) + confidence) / n


@dataclass
class Context:
    session_id: str
    patient: PatientInfo
    caretaker: CaretakerTruth

    sections: dict = field(default_factory=dict)
    current_section: str = "orientation"
    current_question: Optional[str] = None

    memory_summary: str = ""
    global_history: list = field(default_factory=list)
    assessment_complete: bool = False
    stop_reason: Optional[str] = None

    def __post_init__(self):
        for s in ["orientation", "memory", "reasoning"]:
            self.sections[s] = SectionState(name=s)

    @property
    def active_section(self) -> SectionState:
        return self.sections[self.current_section]

    def update_after_answer(self, answer: str, score: float, confidence: float):
        self.active_section.add_interaction(
            question=self.current_question,
            answer=answer,
            score=score,
            confidence=confidence
        )
        self.global_history.append({
            "section": self.current_section,
            "q": self.current_question,
            "a": answer,
        })

    def get_context_snapshot(self) -> dict:
        """Returns serializable context for LLM agents."""
        return {
            "patient": self.patient.model_dump(),
            "caretaker": self.caretaker.model_dump(),
            "current_section": self.current_section,
            "section_state": {
                "question_count": self.active_section.question_count,
                "score": round(self.active_section.score, 3),
                "confidence": round(self.active_section.confidence, 3),
                "history": self.active_section.history[-3:],  # last 3 only
            },
            "memory_summary": self.memory_summary,
            "assessment_complete": self.assessment_complete,
        }

    def get_full_scores(self) -> dict:
        return {
            s: {
                "score": round(sec.score, 3),
                "confidence": round(sec.confidence, 3),
                "questions": sec.question_count,
                "completed": sec.completed,
            }
            for s, sec in self.sections.items()
        }