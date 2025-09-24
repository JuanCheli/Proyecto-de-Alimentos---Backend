from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import time
from api.services.asistente_service import ask_llm_and_execute, LLMError, SQLValidationError, ExecutionError, TimeoutError

router = APIRouter(tags=["asistente"])
logger = logging.getLogger("ask_endpoint")

class AskRequest(BaseModel):
    question: str = Field(..., example="Dame alimentos altos en proteína y bajos en grasa")
    max_results: Optional[int] = Field(10, ge=1, le=500)

@router.post("/ask", response_model=List[Dict[str, Any]])
def ask_endpoint(payload: AskRequest):
    start_time = time.time()
    question = payload.question.strip()
    max_results = payload.max_results

    logger.info(f"Processing ask request: question='{question[:100]}...', max_results={max_results}")

    try:
        results = ask_llm_and_execute(question, max_results=max_results)
        
        elapsed = time.time() - start_time
        logger.info(f"Ask request completed successfully in {elapsed:.2f}s, returned {len(results)} results")
        
        if not results:
            raise HTTPException(status_code=404, detail="No se encontraron resultados para la consulta generada.")

        return results

    except SQLValidationError as e:
        elapsed = time.time() - start_time
        logger.warning(f"SQL validation error after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Consulta no válida: {str(e)}")
        
    except LLMError as e:
        elapsed = time.time() - start_time
        logger.error(f"LLM error after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error del asistente: {str(e)}")
        
    except TimeoutError as e:
        elapsed = time.time() - start_time
        logger.error(f"Timeout error after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(status_code=504, detail=f"Timeout: {str(e)}")
        
    except ExecutionError as e:
        elapsed = time.time() - start_time
        logger.error(f"Execution error after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error ejecutando consulta: {str(e)}")
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"Unexpected error after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
