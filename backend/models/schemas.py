from pydantic import BaseModel
from typing import Optional

class PatientInfo(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str

class CaretakerTruth(BaseModel):
    reported_memory_issues: bool
    duration_of_symptoms: Optional[str] = None
    known_conditions: Optional[list[str]] = []

class AnswerPayload(BaseModel):
    session_id: str
    answer: str

class StartSessionPayload(BaseModel):
    patient: PatientInfo
    caretaker: CaretakerTruth

class WSMessage(BaseModel):
    type: str  # "start" | "answer" | "ping"
    payload: dict