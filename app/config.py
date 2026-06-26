from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_key: str
    supabase_jwt_secret: str

    # Gemini AI
    gemini_api_key: str

    # JSearch (RapidAPI)
    jsearch_api_key: str

    # Apify (optional - for LinkedIn scraping)
    apify_token: str = ""

    # Web Push VAPID keys
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_email: str = "mailto:admin@hireforge.ai"

    # App settings
    daily_job_search_hour: int = 8  # 8 AM UTC
    max_jobs_per_search: int = 50

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
