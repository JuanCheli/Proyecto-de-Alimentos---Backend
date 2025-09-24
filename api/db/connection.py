from supabase import create_client, Client
from api.config import settings

_supabase_url = str(settings.SUPABASE_URL) if settings.SUPABASE_URL is not None else None

supabase: Client | None = None
if _supabase_url and settings.SUPABASE_SERVICE_KEY:
    supabase = create_client(_supabase_url, settings.SUPABASE_SERVICE_KEY)

