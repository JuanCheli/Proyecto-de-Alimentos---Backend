from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from api.services.asistente_service import ask_llm_and_execute, LLMError, SQLValidationError, ExecutionError

router = APIRouter(tags=["asistente"])

class AskRequest(BaseModel):
    question: str = Field(..., example="Dame alimentos altos en proteína y bajos en grasa")
    max_results: Optional[int] = Field(10, ge=1, le=500)

@router.post("/ask", response_model=List[Dict[str, Any]])
def ask_endpoint(payload: AskRequest):
    question = payload.question.strip()
    max_results = payload.max_results

    try:
        results = ask_llm_and_execute(question, max_results=max_results)
    except SQLValidationError as e:
        # el LLM devolvió SQL no permitida -> 400 bad request
        raise HTTPException(status_code=400, detail=str(e))
    except LLMError as e:
        # problema con el LLM -> 503
        raise HTTPException(status_code=503, detail=str(e))
    except ExecutionError as e:
        # problema al ejecutar la query -> 503
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno")

    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para la consulta generada.")

    return results
