"""
Main.py de la API
Incluye:
- Registro de routers (routes/alimentos.py, routes/asistente_ia.py y routes/receta_ia.py)
- Handler para errores de RuntimeError (por ejemplo errores de DB lanzados en repo)
- Endpoint /health que comprueba la conexión básica a la DB (para debug, principalmente)
- Configuración básica de CORS
- Log de rutas al startup (dev)
"""

import os
import logging
from typing import List

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# routers
from api.routes.alimentos import router as alimentos_router

# intentar importar el router del asistente de forma segura
asistente_router = None
try:
    from api.routes.asistente_ia import router as asistente_router
except Exception as e:
    logging.getLogger("api").warning("No se pudo importar api.routes.asistente_ia: %s", e)

# intentar importar el router de recetas de forma segura
receta_router = None
try:
    from api.routes.receta_ia import router as receta_router
except Exception as e:
    logging.getLogger("api").warning("No se pudo importar api.routes.receta_ia: %s", e)

# repo para healthcheck
from api.db.repositories.alimento_repo import get_all as repo_get_all

# configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Leer orígenes CORS desde variable de entorno
_origins = os.getenv("CORS_ORIGINS", "")
if _origins:
    CORS_ORIGINS: List[str] = [o.strip() for o in _origins.split(",") if o.strip()]
else:
    CORS_ORIGINS = ["*"]

app = FastAPI(
    title="API Nutricional",
    version="0.1.0",
    description="API para consultar información nutricional de alimentos (Supabase backend).",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(alimentos_router)

if asistente_router is not None:
    app.include_router(asistente_router, prefix="")
else:
    logger.warning("Router 'asistente_ia' no incluido.")

if receta_router is not None:
    app.include_router(receta_router, prefix="")
else:
    logger.warning("Router 'receta_ia' no incluido.")

# Handler global para RuntimeError
@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    logger.error("RuntimeError capturado: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Error de servicio interno", "error": str(exc)},
    )


@app.get("/", summary="Root", tags=["meta"])
def root():
    return {"message": "API Nutricional - OK", "docs": "/docs", "openapi": "/openapi.json"}


@app.get("/health", summary="Healthcheck", tags=["meta"])
def health():
    try:
        rows = repo_get_all(limit=1, offset=0)
        return {"status": "ok", "db_rows_returned": len(rows)}
    except RuntimeError as e:
        logger.exception("Healthcheck falló al consultar la DB")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "detail": "DB unreachable", "error": str(e)},
        )


@app.on_event("startup")
def log_registered_routes():
    try:
        for r in app.routes:
            methods = ",".join(getattr(r, "methods", []))
            endpoint_name = getattr(r.endpoint, "__name__", r.endpoint.__class__.__name__ if hasattr(r.endpoint, "__class__") else str(r.endpoint))
            logger.info("Route: %s %s -> %s", methods, r.path, endpoint_name)
    except Exception:
        logger.exception("Error listando rutas al startup")
