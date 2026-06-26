from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from app.auth import get_current_user_id
from app.database import supabase

router = APIRouter()


# ── Generic CRUD helpers ─────────────────────────────────────────────────────

def get_user_records(table: str, user_id: str):
    return supabase.table(table).select("*").eq("user_id", user_id).execute().data


def upsert_user_record(table: str, user_id: str, data: dict):
    data["user_id"] = user_id
    return supabase.table(table).upsert(data).execute().data


def delete_user_record(table: str, record_id: str, user_id: str):
    supabase.table(table).delete().eq("id", record_id).eq("user_id", user_id).execute()


# ── Basic Profile ───────────────────────────────────────────────────────────────
@router.get("/")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    data = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
    return data.data[0] if data.data else {}


@router.put("/")
async def upsert_profile(body: dict, user_id: str = Depends(get_current_user_id)):
    body["user_id"] = user_id
    result = supabase.table("profiles").upsert(body, on_conflict="user_id").execute()
    return result.data[0] if result.data else body


# ── Work Experience ───────────────────────────────────────────────────────────
@router.get("/experience")
async def get_experience(user_id: str = Depends(get_current_user_id)):
    return get_user_records("work_experiences", user_id)


@router.post("/experience")
async def add_experience(body: dict, user_id: str = Depends(get_current_user_id)):
    return upsert_user_record("work_experiences", user_id, body)


@router.delete("/experience/{record_id}")
async def delete_experience(record_id: str, user_id: str = Depends(get_current_user_id)):
    delete_user_record("work_experiences", record_id, user_id)
    return {"deleted": record_id}


# ── Education ───────────────────────────────────────────────────────────────────
@router.get("/education")
async def get_education(user_id: str = Depends(get_current_user_id)):
    return get_user_records("education", user_id)


@router.post("/education")
async def add_education(body: dict, user_id: str = Depends(get_current_user_id)):
    return upsert_user_record("education", user_id, body)


@router.delete("/education/{record_id}")
async def delete_education(record_id: str, user_id: str = Depends(get_current_user_id)):
    delete_user_record("education", record_id, user_id)
    return {"deleted": record_id}


# ── Skills ───────────────────────────────────────────────────────────────────────
@router.get("/skills")
async def get_skills(user_id: str = Depends(get_current_user_id)):
    return get_user_records("skills", user_id)


@router.put("/skills")
async def update_skills(body: dict, user_id: str = Depends(get_current_user_id)):
    return upsert_user_record("skills", user_id, body)


# ── Projects ─────────────────────────────────────────────────────────────────────
@router.get("/projects")
async def get_projects(user_id: str = Depends(get_current_user_id)):
    return get_user_records("projects", user_id)


@router.post("/projects")
async def add_project(body: dict, user_id: str = Depends(get_current_user_id)):
    return upsert_user_record("projects", user_id, body)


@router.delete("/projects/{record_id}")
async def delete_project(record_id: str, user_id: str = Depends(get_current_user_id)):
    delete_user_record("projects", record_id, user_id)
    return {"deleted": record_id}


# ── Certifications ───────────────────────────────────────────────────────────
@router.get("/certifications")
async def get_certifications(user_id: str = Depends(get_current_user_id)):
    return get_user_records("certifications", user_id)


@router.post("/certifications")
async def add_certification(body: dict, user_id: str = Depends(get_current_user_id)):
    return upsert_user_record("certifications", user_id, body)


@router.delete("/certifications/{record_id}")
async def delete_certification(record_id: str, user_id: str = Depends(get_current_user_id)):
    delete_user_record("certifications", record_id, user_id)
    return {"deleted": record_id}
