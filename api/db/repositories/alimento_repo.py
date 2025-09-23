from api.db.connection import supabase
from typing import List, Optional, Dict, Any

TABLE = "alimentos"

def get_all(limit: int = 100, offset: int = 0) -> List[dict]:
    resp = supabase.table(TABLE).select("*").limit(limit).offset(offset).execute()
    # resp es un dict-like, se accede como atributo o clave
    return resp.data or []


def get_by_codigo(codigo: int) -> Optional[dict]:
    resp = supabase.table(TABLE).select("*").eq("codigomex2", codigo).maybe_single().execute()
    return resp.data  # dict o None


def insert_alimento(obj: dict) -> dict:
    resp = supabase.table(TABLE).insert(obj).execute()
    return resp.data[0] if resp.data else None



def search_alimentos(filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[dict]:
    field_map = {
        "calorias": "energ_kcal",
        "carbohidratos": "carbohydrt",
        "proteina": "protein",
        "lipidos": "lipid_tot",
    }

    qb = supabase.table(TABLE).select("*")
    for k, v in filters.items():
        if v is None:
            continue
        if k.startswith("min_"):
            raw = k[4:]
            col = field_map.get(raw, raw)
            qb = qb.gte(col, v)
        elif k.startswith("max_"):
            raw = k[4:]
            col = field_map.get(raw, raw)
            qb = qb.lte(col, v)
        else:
            col = field_map.get(k, k)
            qb = qb.eq(col, v)

    qb = qb.limit(limit).offset(offset)
    resp = qb.execute()
    return resp.data or []
