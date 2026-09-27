import json
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.job import Job
from app.models.candidate import Candidate
from app.utils.file_parser import extract_text
from app.services.llm_service import extract_candidate_profile

router = APIRouter()


@router.post("/resumes")
async def upload_resume(
    job_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id {job_id} not found")

    raw_text = await extract_text(file)

    extracted = extract_candidate_profile(raw_text)

    new_candidate = Candidate(
        job_id=job_id,
        raw_text=raw_text,
        name=extracted.get("name", ""),
        skills=json.dumps(extracted.get("skills", [])),
        experience=extracted.get("experience", ""),
        education=extracted.get("education", ""),
        projects=json.dumps(extracted.get("projects", [])),
        certifications=json.dumps(extracted.get("certifications", []))
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return {
        "id": new_candidate.id,
        "job_id": new_candidate.job_id,
        "name": extracted.get("name", ""),
        "skills": extracted.get("skills", []),
        "experience": extracted.get("experience", ""),
        "education": extracted.get("education", ""),
        "projects": extracted.get("projects", []),
        "certifications": extracted.get("certifications", []),
        "message": "Resume uploaded and processed successfully"
    }