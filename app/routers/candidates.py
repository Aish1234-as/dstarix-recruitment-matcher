import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.candidate import Candidate

router = APIRouter()


@router.get("/candidates")
def list_candidates(job_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Candidate)
    if job_id:
        query = query.filter(Candidate.job_id == job_id)
    candidates = query.all()

    return [
        {
            "id": c.id,
            "job_id": c.job_id,
            "name": c.name,
            "skills": json.loads(c.skills or "[]"),
            "experience": c.experience,
            "education": c.education,
            "match_score": c.match_score,
            "matching_skills": json.loads(c.matching_skills or "[]"),
            "missing_skills": json.loads(c.missing_skills or "[]"),
        }
        for c in candidates
    ]


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with id {candidate_id} not found")

    return {
        "id": candidate.id,
        "job_id": candidate.job_id,
        "name": candidate.name,
        "skills": json.loads(candidate.skills or "[]"),
        "experience": candidate.experience,
        "education": candidate.education,
        "projects": json.loads(candidate.projects or "[]"),
        "certifications": json.loads(candidate.certifications or "[]"),
        "match_score": candidate.match_score,
        "matching_skills": json.loads(candidate.matching_skills or "[]"),
        "missing_skills": json.loads(candidate.missing_skills or "[]"),
        "ai_explanation": candidate.ai_explanation
    }