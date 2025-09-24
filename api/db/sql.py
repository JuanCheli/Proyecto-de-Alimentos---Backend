from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import text, create_engine
from api.config import settings
import logging

logger = logging.getLogger(__name__)

def _normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            try:
                out[k] = float(v)
            except Exception:
                out[k] = v
        else:
            out[k] = v
    return out

def execute_sql(sql: str, params: Optional[dict] = None) -> List[Dict[str, Any]]:
    """
    Ejecuta SQL creando una conexión fresca para evitar problemas de timeout.
    útil después de operaciones lentas como llamadas al LLM.
    """
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL no configurada: no se puede ejecutar SQL directo.")

    # Crear engine temporal con configuración optimizada para Supabase
    engine_kwargs = {
        "echo": False,
        "pool_size": 1,  # Solo una conexión para esta operación
        "max_overflow": 0,
        "pool_pre_ping": True,  # Verificar conexión antes de usar
        "pool_recycle": -1,     # No reciclar (conexión temporal)
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 10,
            "application_name": "render_backend_ask",
        }
    }
    
    temp_engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    
    try:
        with temp_engine.connect() as conn:
            if params:
                result = conn.execute(text(sql), params)
            else:
                result = conn.execute(text(sql))
            
            rows = [_normalize_row(dict(r)) for r in result.mappings().all()]
            return rows
            
    except Exception as e:
        logger.error(f"Error ejecutando SQL: {str(e)}")
        raise RuntimeError("Error ejecutando la consulta SQL.") from e
    finally:
        # Limpiar el engine temporal
        temp_engine.dispose()