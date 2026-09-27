from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from datetime import datetime
from app.models.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    name = Column(String)
    raw_text = Column(Text, nullable=False)
    skills = Column(Text)
    experience = Column(String)
    education = Column(String)
    projects = Column(Text)
    certifications = Column(Text)

    match_score = Column(Float, default=0.0)
    matching_skills = Column(Text)
    missing_skills = Column(Text)
    ai_explanation = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)