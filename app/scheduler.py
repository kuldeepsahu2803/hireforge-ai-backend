import asyncio
import logging
from datetime import datetime
import httpx
from app.database import supabase
from app.config import settings

logger = logging.getLogger(__name__)


async def fetch_jobs_for_user(user_id: str, search_query: str, location: str):
    """Fetch new jobs from JSearch for a single user's saved search."""
    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": f"{search_query} in {location}",
        "num_pages": "1",
        "date_posted": "today",
    }
    headers = {
        "X-RapidAPI-Key": settings.jsearch_api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        jobs = data.get("data", [])
        new_count = 0

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
                "source": "jsearch",
                "status": "new",
            }
            result = (
                supabase.table("jobs")
                .upsert(record, on_conflict="user_id,job_id")
                .execute()
            )
            if result.data:
                new_count += 1

        logger.info(f"Daily fetch: {new_count} new jobs for user {user_id}")
        return new_count

    except Exception as e:
        logger.error(f"Daily job fetch failed for user {user_id}: {e}")
        return 0


async def daily_job_fetch():
    """Run daily job fetch for all users who have saved search preferences."""
    logger.info(f"Starting daily job fetch at {datetime.utcnow()}")

    # Get all users with saved search prefs
    result = supabase.table("job_search_preferences").select("*").execute()
    prefs = result.data or []

    tasks = [
        fetch_jobs_for_user(
            pref["user_id"],
            pref.get("search_query", "software engineer"),
            pref.get("location", "India")
        )
        for pref in prefs
    ]

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_new = sum(r for r in results if isinstance(r, int))
        logger.info(f"Daily fetch complete: {total_new} total new jobs across {len(prefs)} users")


async def start_scheduler():
    """Infinite loop running daily fetch at the configured hour."""
    logger.info("Scheduler started")
    while True:
        now = datetime.utcnow()
        target_hour = settings.daily_job_search_hour

        # Calculate seconds until next run
        if now.hour < target_hour:
            wait_seconds = (target_hour - now.hour) * 3600 - now.minute * 60 - now.second
        else:
            # Next day
            wait_seconds = (24 - now.hour + target_hour) * 3600 - now.minute * 60 - now.second

        logger.info(f"Next daily job fetch in {wait_seconds // 3600}h {(wait_seconds % 3600) // 60}m")
        await asyncio.sleep(wait_seconds)
        await daily_job_fetch()
