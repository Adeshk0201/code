from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Patient(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    sessions = relationship("Session", back_populates="patient")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    stop_reason = Column(String, nullable=True)
    total_questions = Column(Integer, default=0)
    caretaker_info = Column(JSON, default={})
    patient = relationship("Patient", back_populates="sessions")
    section_scores = relationship("SectionScore", back_populates="session")
    report = relationship("Report", back_populates="session", uselist=False)
    interactions = relationship("Interaction", back_populates="session")


class SectionScore(Base):
    __tablename__ = "section_scores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    section_name = Column(String)
    score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    question_count = Column(Integer, default=0)
    observations = Column(Text, nullable=True)
    session = relationship("Session", back_populates="section_scores")


class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    section = Column(String)
    question = Column(Text)
    answer = Column(Text)
    score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    timestamp = Column(DateTime, server_default=func.now())
    session = relationship("Session", back_populates="interactions")


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    report_text = Column(Text)
    risk_level = Column(String)
    recommendations = Column(JSON, default=[])
    consistency_score = Column(Float, default=1.0)
    consistency_mismatches = Column(JSON, default=[])
    created_at = Column(DateTime, server_default=func.now())
    session = relationship("Session", back_populates="report")