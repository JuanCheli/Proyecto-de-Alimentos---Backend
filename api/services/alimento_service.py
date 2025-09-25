from typing import List, Dict, Any
from api.db.repositories.alimento_repo import (
    get_all,
    get_by_codigo,
    insert_alimento,
    search_alimentos,
    search_by_nombre,
)
from api.schemas.alimento_schema import AlimentoCreate

def list_alimentos(limit: int = 100, offset: int = 0):
    return get_all(limit=limit, offset=offset)

def create_alimento(payload: AlimentoCreate):
    created = insert_alimento(payload.dict())
    if not created:
        raise RuntimeError("No se pudo crear el alimento")
    return created

def find_alimento(codigo: int):
    return get_by_codigo(codigo)

def search_alimentos_db(filters: Dict[str, Any], limit: int = 100, offset: int = 0):
    return search_alimentos(filters=filters, limit=limit, offset=offset)

def search_alimentos_nombre(nombre: str, limit: int = 50, offset: int = 0):
    return search_by_nombre(nombre=nombre, limit=limit, offset=offset)
