import json
from groq import Groq
from fastapi import HTTPException
from app.utils.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)
MODEL = "openai/gpt-oss-120b"


def extract_job_requirements(jd_text: str) -> dict:
    """Extract structured requirements from a job description using the LLM."""
    prompt = f"""
You are an expert technical recruiter. Extract structured information from the job description below.

Return ONLY valid JSON, no preamble, no markdown formatting, in exactly this shape:
{{
  "required_skills": ["skill1", "skill2"],
  "required_experience": "e.g. 3+ years",
  "required_education": "e.g. B.Tech in Computer Science",
  "nice_to_have_skills": ["skill1", "skill2"]
}}

Job Description:
\"\"\"
{jd_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw_output = response.choices[0].message.content.strip()

        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw_output)
        return parsed

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="LLM returned invalid JSON while extracting job requirements"
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM API call failed: {str(e)}"
        )


def extract_candidate_profile(resume_text: str) -> dict:
    """Extract structured candidate profile from resume text using the LLM."""
    prompt = f"""
You are an expert resume parser. Extract structured information from the resume below.

Return ONLY valid JSON, no preamble, no markdown formatting, in exactly this shape:
{{
  "name": "Candidate Name",
  "skills": ["Python", "FastAPI", "SQL"],
  "experience": "e.g. 3 years",
  "education": "e.g. B.Tech Computer Science",
  "projects": ["project description 1", "project description 2"],
  "certifications": ["certification 1"]
}}

If any field is not found, use an empty string or empty list as appropriate.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw_output = response.choices[0].message.content.strip()

        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw_output)
        return parsed

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="LLM returned invalid JSON while extracting candidate profile"
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM API call failed: {str(e)}"
        )