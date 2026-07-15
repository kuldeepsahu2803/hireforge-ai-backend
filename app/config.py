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

    # Apify (optional)
    apify_token: str = ""

    # VAPID keys (optional)
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_email: str = "mailto:admin@hireforge.ai"

    # App settings
    daily_job_search_hour: int = 8
    max_jobs_per_search: int = 50

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
