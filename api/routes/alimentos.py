from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas.alimento_schema import AlimentoCreate, AlimentoRead, AlimentoFilter
from api.services.alimento_service import (
    list_alimentos,
    create_alimento,
    find_alimento,
    search_alimentos_db,
)

router = APIRouter(tags=["alimentos"])

@router.get("/alimentos", response_model=List[AlimentoRead])
def read_alimentos(limit: int = 100, offset: int = 0):
    """
    Endpoint para listar alimentos.
    """
    return list_alimentos(limit=limit, offset=offset)
@router.get("/alimento/{codigo}", response_model=AlimentoRead)
def read_alimento(codigo: int):
    try:
        item = find_alimento(codigo)
    except RuntimeError as e:
        # error de DB
        raise HTTPException(status_code=503, detail=str(e))
    if not item:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")
    return item

@router.post("/buscar", response_model=List[AlimentoRead])
def buscar_alimentos(filters: AlimentoFilter, limit: int = 100, offset: int = 0):
    fdict = {k: v for k, v in filters.dict().items() if v is not None}
    try:
        results = search_alimentos_db(fdict, limit=limit, offset=offset)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return results


@router.post("/alimento", response_model=AlimentoRead, status_code=201)
def create_alimento_endpoint(item: AlimentoCreate):
    """
    Endpoint para crear alimento.
    """
    created = create_alimento(item)
    if not created:
        raise HTTPException(status_code=400, detail="No se pudo crear el alimento")
    return created