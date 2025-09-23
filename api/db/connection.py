from supabase import create_client, Client
from api.config import settings

# Aca es donde se crea el cliente de Supabase usando la SERVICE_KEY (que es la que tiene permisos de RLS)
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY,
)
