import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.job import Job
from app.models.candidate import Candidate
from app.services.scoring_service import calculate_candidate_score
from app.services.llm_service import client, MODEL

router = APIRouter()


def generate_ai_explanation(job_title: str, matching_skills: list, missing_skills: list, score: float) -> str:
    """Generate a short AI explanation of the candidate's fit."""
    prompt = f"""
You are a recruiter assistant. In 3-4 sentences, explain this candidate's suitability for the "{job_title}" role.

Match score: {score}%
Matching skills: {', '.join(matching_skills) if matching_skills else 'None'}
Missing skills: {', '.join(missing_skills) if missing_skills else 'None'}

Be concise, specific, and mention both strengths and gaps.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "AI explanation unavailable due to an LLM error."


@router.post("/match/{job_id}")
def match_candidates(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id {job_id} not found")

    candidates = db.query(Candidate).filter(Candidate.job_id == job_id).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found for this job")

    job_dict = {
        "required_skills": json.loads(job.required_skills or "[]"),
        "required_experience": job.required_experience or "",
        "required_education": job.required_education or "",
    }

    results = []

    for candidate in candidates:
        candidate_dict = {
            "skills": json.loads(candidate.skills or "[]"),
            "experience": candidate.experience or "",
            "education": candidate.education or "",
            "projects": json.loads(candidate.projects or "[]"),
        }

        score_result = calculate_candidate_score(job_dict, candidate_dict)

        explanation = generate_ai_explanation(
            job.title,
            score_result["matching_skills"],
            score_result["missing_skills"],
            score_result["match_score"]
        )

        candidate.match_score = score_result["match_score"]
        candidate.matching_skills = json.dumps(score_result["matching_skills"])
        candidate.missing_skills = json.dumps(score_result["missing_skills"])
        candidate.ai_explanation = explanation

        db.add(candidate)

        results.append({
            "candidate_id": candidate.id,
            "name": candidate.name,
            "match_score": score_result["match_score"],
            "matching_skills": score_result["matching_skills"],
            "missing_skills": score_result["missing_skills"],
            "breakdown": score_result["breakdown"],
            "ai_explanation": explanation
        })

    db.commit()

    results.sort(key=lambda x: x["match_score"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    return {
        "job_id": job_id,
        "job_title": job.title,
        "total_candidates": len(results),
        "ranking": results
    }


@router.get("/ranking/{job_id}")
def get_ranking(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id {job_id} not found")

    candidates = db.query(Candidate).filter(Candidate.job_id == job_id).order_by(Candidate.match_score.desc()).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found for this job")

    return {
        "job_id": job_id,
        "job_title": job.title,
        "ranking": [
            {
                "rank": i + 1,
                "candidate_id": c.id,
                "name": c.name,
                "match_score": c.match_score,
                "matching_skills": json.loads(c.matching_skills or "[]"),
                "missing_skills": json.loads(c.missing_skills or "[]"),
            }
            for i, c in enumerate(candidates)
        ]
    }