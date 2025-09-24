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
    try:
        items = list_alimentos(limit=limit, offset=offset)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Error al obtener alimentos: {str(e)}")
    if not items:
        raise HTTPException(status_code=404, detail="No se encontraron alimentos")
    return items


@router.get("/alimento/{codigo}", response_model=AlimentoRead)
def read_alimento(codigo: int):
    item = find_alimento(codigo)

    if not item:
        raise HTTPException(status_code=404, detail=f"Alimento con código {codigo} no encontrado")

    return item




@router.post("/buscar", response_model=List[AlimentoRead])
def buscar_alimentos(filters: AlimentoFilter, limit: int = 100, offset: int = 0):
    """
    Endpoint para buscar alimentos aplicando filtros.
    """
    fdict = {k: v for k, v in filters.dict().items() if v is not None}
    try:
        results = search_alimentos_db(fdict, limit=limit, offset=offset)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Error al buscar alimentos: {str(e)}")
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron alimentos con los filtros aplicados")
    return results


@router.post("/alimento", response_model=AlimentoRead, status_code=201)
def create_alimento_endpoint(item: AlimentoCreate):
    """
    Endpoint para crear alimento.
    """
    try:
        created = create_alimento(item)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Error al crear alimento: {str(e)}")

    if not created:
        raise HTTPException(status_code=400, detail="No se pudo crear el alimento")
    return created
