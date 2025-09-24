from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from api.db.session import get_engine
import logging
import time

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

def execute_sql(sql: str, params: Optional[dict] = None, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Ejecuta SQL con reintentos, usando el mismo engine que otros endpoints exitosos.
    """
    engine = get_engine()
    if engine is None:
        raise RuntimeError("DATABASE_URL no configurada: no se puede ejecutar SQL directo.")

    for attempt in range(max_retries):
        try:
            # Usar una nueva conexión para cada intento
            with engine.connect() as conn:
                if params:
                    result = conn.execute(text(sql), params)
                else:
                    result = conn.execute(text(sql))
                
                rows = [_normalize_row(dict(r)) for r in result.mappings().all()]
                logger.info(f"SQL executed successfully on attempt {attempt + 1}, returned {len(rows)} rows")
                return rows
                
        except Exception as e:
            logger.warning(f"SQL execution attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            
            if attempt == max_retries - 1:  # Último intento
                logger.error(f"SQL execution failed after {max_retries} attempts")
                raise RuntimeError("Error ejecutando la consulta SQL.") from e
            
            # Esperar antes del siguiente intento
            time.sleep(1.0 * (attempt + 1))  # 1s, 2s, 3s...