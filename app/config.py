import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class Settings:
    supabase_url: str = os.environ.get("SUPABASE_URL", "")
    supabase_service_key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")
    supabase_jwt_secret: str = os.environ.get("SUPABASE_JWT_SECRET", "")
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    jsearch_api_key: str = os.environ.get("JSEARCH_API_KEY", "")
    apify_token: str = os.environ.get("APIFY_TOKEN", "")
    vapid_private_key: str = os.environ.get("VAPID_PRIVATE_KEY", "")
    vapid_public_key: str = os.environ.get("VAPID_PUBLIC_KEY", "")
    vapid_email: str = os.environ.get("VAPID_EMAIL", "mailto:admin@hireforge.ai")
    daily_job_search_hour: int = int(os.environ.get("DAILY_JOB_SEARCH_HOUR", "8"))
    max_jobs_per_search: int = int(os.environ.get("MAX_JOBS_PER_SEARCH", "50"))

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
