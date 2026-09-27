from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str):
    """Convert a piece of text into an embedding vector."""
    return model.encode(text, convert_to_tensor=True)


def compute_similarity(text1: str, text2: str) -> float:
    """Return a similarity score (0 to 1) between two pieces of text."""
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)
    similarity = util.cos_sim(embedding1, embedding2)
    return float(similarity[0][0])


def compute_skill_match(required_skills: list, candidate_skills: list, threshold: float = 0.6):
    """
    Compare required skills against candidate skills using semantic similarity.
    Returns matching skills, missing skills, and an overall skill match score.
    """
    if not required_skills:
        return {"matching_skills": [], "missing_skills": [], "score": 0.0}

    matching_skills = []
    missing_skills = []

    for req_skill in required_skills:
        best_match_score = 0.0
        for cand_skill in candidate_skills:
            score = compute_similarity(req_skill, cand_skill)
            if score > best_match_score:
                best_match_score = score

        if best_match_score >= threshold:
            matching_skills.append(req_skill)
        else:
            missing_skills.append(req_skill)

    score = len(matching_skills) / len(required_skills) if required_skills else 0.0

    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "score": round(score, 2)
    }