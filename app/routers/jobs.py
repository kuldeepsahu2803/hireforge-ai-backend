from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import httpx
from app.auth import get_current_user_id
from app.database import supabase
from app.config import settings
from pydantic import BaseModel

router = APIRouter()


class JobSearchRequest(BaseModel):
    query: str
    location: str = "India"
    employment_type: Optional[str] = None
    date_posted: Optional[str] = "month"


class JobStatusUpdate(BaseModel):
    status: str  # applied, interview, offer, rejected, saved


# ── Search jobs via JSearch API ──────────────────────────────────────────────
@router.post("/search")
async def search_jobs(
    request: JobSearchRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Search jobs using JSearch (RapidAPI) and persist results to Supabase."""
    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": f"{request.query} in {request.location}",
        "num_pages": "2",
        "date_posted": request.date_posted or "month",
    }
    if request.employment_type:
        params["employment_types"] = request.employment_type

    headers = {
        "X-RapidAPI-Key": settings.jsearch_api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    jobs = data.get("data", [])
    saved = []

    for job in jobs:
        record = {
            "user_id": user_id,
            "job_id": job.get("job_id"),
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": job.get("job_city", "") + ", " + job.get("job_country", ""),
            "description": job.get("job_description", "")[:5000],
            "url": job.get("job_apply_link"),
            "employment_type": job.get("job_employment_type"),
            "salary_min": job.get("job_min_salary"),
            "salary_max": job.get("job_max_salary"),
            "source": "jsearch",
            "status": "new",
        }
        # Upsert to avoid duplicates
        result = (
            supabase.table("jobs")
            .upsert(record, on_conflict="user_id,job_id")
            .execute()
        )
        saved.append(record)

    return {"fetched": len(jobs), "saved": len(saved)}


# ── Get saved jobs ────────────────────────────────────────────────────────────
@router.get("/")
async def get_jobs(
    status: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
):
    """Return all jobs for the current user, optionally filtered by status."""
    query = supabase.table("jobs").select("*").eq("user_id", user_id)
    if status:
        query = query.eq("status", status)
    result = query.order("created_at", desc=True).execute()
    return result.data


# ── Update job status (Kanban) ────────────────────────────────────────────────
@router.patch("/{job_id}/status")
async def update_job_status(
    job_id: str,
    body: JobStatusUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Move a job card to a new Kanban column."""
    result = (
        supabase.table("jobs")
        .update({"status": body.status})
        .eq("id", job_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")
    return result.data[0]


# ── Delete a job ───────────────────────────────────────────────────────────────
@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
):
    supabase.table("jobs").delete().eq("id", job_id).eq("user_id", user_id).execute()
    return {"deleted": job_id}
