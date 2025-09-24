from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from api.services.receta_service import crear_receta, RecetaError

router = APIRouter(tags=["asistente"])

class Ingrediente(BaseModel):
    codigomex2: int
    cantidad_g: float = 100

class RecetaRequest(BaseModel):
    ingredientes: List[Ingrediente]

@router.post("/receta", response_model=Dict)
def receta_endpoint(payload: RecetaRequest):
    try:
        receta = crear_receta([i.dict() for i in payload.ingredientes])
    except RecetaError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno")
    return receta
