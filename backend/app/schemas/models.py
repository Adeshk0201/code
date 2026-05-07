from pydantic import BaseModel
from typing import List, Dict

class ContextModel(BaseModel):
    patient_info: Dict = {}
    caretaker_truth: Dict = {}

    current_section: str = "Orientation"

    question_count: int = 0
    max_questions: int = 5

    confidence: float = 0.0

    history: List = []

    section_scores: Dict = {}

    memory_summary: str = ""

    stop: bool = False