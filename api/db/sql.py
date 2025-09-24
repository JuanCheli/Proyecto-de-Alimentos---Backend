
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from api.db.session import SessionLocal
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
    Ejecuta SQL usando SessionLocal para mantener consistencia con otros endpoints.
    """
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurada: no se puede ejecutar SQL directo.")

    db = SessionLocal()
    try:
        if params:
            result = db.execute(text(sql), params)
        else:
            result = db.execute(text(sql))
        
        rows = [_normalize_row(dict(r)) for r in result.mappings().all()]
        return rows
        
    except Exception as e:
        logger.error(f"Error ejecutando SQL: {str(e)}")
        raise RuntimeError("Error ejecutando la consulta SQL.") from e
    finally:
        db.close()