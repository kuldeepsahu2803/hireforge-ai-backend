from supabase import create_client, Client
from app.config import settings
from functools import lru_cache


@lru_cache
def get_supabase() -> Client:
    """Return a Supabase client using the service role key (bypasses RLS for server-side ops)."""
    return create_client(settings.supabase_url, settings.supabase_service_key)


# Singleton instance
supabase: Client = get_supabase()
