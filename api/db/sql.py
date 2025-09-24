from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from api.db.session import get_engine

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
    engine = get_engine()
    if engine is None:
        raise RuntimeError("DATABASE_URL no configurada: no se puede ejecutar SQL directo.")

    try:
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(sql), params)
            else:
                result = conn.execute(text(sql))
            rows = [ _normalize_row(dict(r)) for r in result.mappings().all() ]
            return rows
    except Exception as e:
        raise RuntimeError("Error ejecutando la consulta SQL.") from e
