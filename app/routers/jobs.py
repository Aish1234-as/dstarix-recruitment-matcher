import json
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.job import Job
from app.utils.file_parser import extract_text
from app.services.llm_service import extract_job_requirements

router = APIRouter()


@router.post("/jobs")
async def create_job(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Job title is required")

    raw_text = await extract_text(file)

    extracted = extract_job_requirements(raw_text)

    new_job = Job(
        title=title,
        raw_text=raw_text,
        required_skills=json.dumps(extracted.get("required_skills", [])),
        required_experience=extracted.get("required_experience", ""),
        required_education=extracted.get("required_education", "")
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "id": new_job.id,
        "title": new_job.title,
        "required_skills": extracted.get("required_skills", []),
        "required_experience": extracted.get("required_experience", ""),
        "required_education": extracted.get("required_education", ""),
        "message": "Job description uploaded and processed successfully"
    }


@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "required_skills": json.loads(j.required_skills or "[]"),
            "required_experience": j.required_experience,
            "required_education": j.required_education
        }
        for j in jobs
    ]