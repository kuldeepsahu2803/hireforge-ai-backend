from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from app.auth import get_current_user_id
from app.database import supabase
from app.config import settings
import json

genai.configure(api_key=settings.gemini_api_key)
router = APIRouter()


class TailorRequest(BaseModel):
    job_description: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class SaveTailoredRequest(BaseModel):
    job_id: Optional[str] = None
    job_title: str
    company_name: str
    original_score: int
    tailored_score: int
    tailored_summary: str
    tailored_experience: list
    keywords_added: list
    gaps: list
    full_tailored_resume: str


def build_master_profile(user_id: str) -> dict:
    """Assemble master profile from all profile tables."""
    profile = {}

    tables = [
        "profiles", "work_experiences", "education", "projects",
        "skills", "certifications", "publications"
    ]

    for table in tables:
        result = supabase.table(table).select("*").eq("user_id", user_id).execute()
        profile[table] = result.data

    return profile


@router.post("/tailor")
async def tailor_resume(
    request: TailorRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Use Gemini AI to tailor resume to a job description."""
    master = build_master_profile(user_id)

    if not master.get("profiles"):
        raise HTTPException(status_code=400, detail="Complete your profile before tailoring")

    prompt = f"""You are an expert ATS resume writer. Your task is to tailor a resume for a specific job.

CRITICAL RULES:
1. NEVER fabricate, invent, or add any experience, skills, or achievements not present in the master profile
2. Only REFRAME and EMPHASIZE existing factual data to match the job description
3. Use action verbs and quantifiable language from the existing data
4. Match ATS keywords from the JD to existing profile content

MASTER PROFILE:
{json.dumps(master, indent=2)}

JOB DESCRIPTION:
{request.job_description}

Job Title: {request.job_title or 'Not specified'}
Company: {request.company_name or 'Not specified'}

Provide a JSON response with this exact structure:
{{
  "ats_score_original": <integer 0-100>,
  "ats_score_tailored": <integer 0-100>,
  "tailored_summary": "<2-3 sentences professional summary reframed for this role>",
  "tailored_experience": [
    {{
      "company": "<company from master profile>",
      "role": "<role from master profile>",
      "bullets": ["<reframed bullet 1>", "<reframed bullet 2>"]
    }}
  ],
  "keywords_matched": ["<keyword1>", "<keyword2>"],
  "keywords_missing": ["<gap keyword1>"],
  "gaps": ["<gap analysis item 1>"],
  "cover_letter_opening": "<2-sentence compelling opening for a cover letter>"
}}"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")

    return result


@router.post("/save")
async def save_tailored_resume(
    body: SaveTailoredRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Persist a tailored resume version to Supabase."""
    record = {
        "user_id": user_id,
        **body.dict()
    }
    result = supabase.table("tailored_resumes").insert(record).execute()
    return result.data[0] if result.data else {"status": "saved"}


@router.get("/history")
async def get_tailored_history(
    user_id: str = Depends(get_current_user_id),
):
    """Get all previously tailored resumes for the user."""
    result = (
        supabase.table("tailored_resumes")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data
