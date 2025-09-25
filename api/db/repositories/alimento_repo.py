from api.db.connection import supabase
from typing import List, Optional, Dict, Any

TABLE = "alimentos"

def get_all(limit: int = 100, offset: int = 0) -> List[dict]:
    resp = supabase.table(TABLE).select("*").limit(limit).offset(offset).execute()
    # resp es un dict-like, se accede como atributo o clave
    return resp.data or []


def get_by_codigo(codigo: int):
    resp = supabase.table(TABLE).select("*").eq("codigomex2", codigo).limit(1).execute()

    # Si no hay filas
    if not resp.data or len(resp.data) == 0:
        return None

    # Si encuentra 1 fila
    return resp.data[0]


def get_by_codigos(codigos: List[int]) -> List[dict]:
    """
    Devuelve todos los alimentos cuyo codigomex2 esté en la lista `codigos`.
    """
    if not codigos:
        return []

    resp = supabase.table(TABLE).select("*").in_("codigomex2", codigos).execute()
    return resp.data or []


def search_by_nombre(nombre: str, limit: int = 50, offset: int = 0) -> List[dict]:
    """
    Busca alimentos cuyo nombre_del_alimento contenga el texto (esto, para que hacer recetas en el front sea mas facil).
    Ej: "ALGOD" -> "ACEITE DE ALGODON"
    """
    resp = (
        supabase.table(TABLE)
        .select("*")
        .ilike("nombre_del_alimento", f"%{nombre}%")
        .limit(limit)
        .offset(offset)
        .execute()
    )
    return resp.data or []



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
