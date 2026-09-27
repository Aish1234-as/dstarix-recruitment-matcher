from app.services.embedding_service import compute_skill_match, compute_similarity


def calculate_candidate_score(job: dict, candidate: dict) -> dict:
    """
    Calculate a weighted match score between a job and a candidate.
    Weights: Skills 40%, Experience 25%, Projects 20%, Education 10%, Additional Skills 5%
    """

    required_skills = job.get("required_skills", [])
    candidate_skills = candidate.get("skills", [])

    skill_result = compute_skill_match(required_skills, candidate_skills)
    skill_score = skill_result["score"]

    experience_score = compute_similarity(
        job.get("required_experience", ""),
        candidate.get("experience", "")
    ) if job.get("required_experience") and candidate.get("experience") else 0.0

    projects_text = " ".join(candidate.get("projects", []))
    projects_score = compute_similarity(
        " ".join(required_skills),
        projects_text
    ) if required_skills and projects_text else 0.0

    education_score = compute_similarity(
        job.get("required_education", ""),
        candidate.get("education", "")
    ) if job.get("required_education") and candidate.get("education") else 0.0

    additional_skills = [s for s in candidate_skills if s not in skill_result["matching_skills"]]
    additional_skills_score = min(len(additional_skills) / 5, 1.0)

    final_score = (
        skill_score * 0.40 +
        experience_score * 0.25 +
        projects_score * 0.20 +
        education_score * 0.10 +
        additional_skills_score * 0.05
    )

    return {
        "match_score": round(final_score * 100, 2),
        "matching_skills": skill_result["matching_skills"],
        "missing_skills": skill_result["missing_skills"],
        "breakdown": {
            "skills_score": round(skill_score * 100, 2),
            "experience_score": round(experience_score * 100, 2),
            "projects_score": round(projects_score * 100, 2),
            "education_score": round(education_score * 100, 2),
            "additional_skills_score": round(additional_skills_score * 100, 2),
        }
    }