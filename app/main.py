from fastapi import FastAPI
from app.models.database import Base, engine
from app.models import job, candidate  # noqa: F401
from app.routers import jobs, resumes, match, candidates

app = FastAPI(title="AI Recruitment & Candidate Matching Platform")

Base.metadata.create_all(bind=engine)

app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(match.router)
app.include_router(candidates.router)


@app.get("/")
def root():
    return {"message": "AI Recruitment & Candidate Matching Platform is running"}