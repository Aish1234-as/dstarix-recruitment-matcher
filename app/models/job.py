from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.models.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    required_skills = Column(Text)
    required_experience = Column(String)
    required_education = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)