"""
Main.py de la API
Incluye:
- Registro de routers (routes/alimentos.py y routes/asistente_ia.py)
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

# intentar importar el router del asistente de forma segura (no romper startup si falla)
asistente_router = None
try:
    from api.routes.asistente_ia import router as asistente_router  # optional
except Exception as e:
    # no hacemos raise; lo registramos y el endpoint /ask no se montará
    logging.getLogger("api").warning("No se pudo importar api.routes.asistente_ia: %s", e)
    asistente_router = None

# repo para healthcheck
from api.db.repositories.alimento_repo import get_all as repo_get_all

# configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Leer orígenes CORS desde variable de entorno (en este caso no la tenemos, pero es buena practica)
_origins = os.getenv("CORS_ORIGINS", "")
if _origins:
    # separa por comas si pasas multiples origenes
    CORS_ORIGINS: List[str] = [o.strip() for o in _origins.split(",") if o.strip()]
else:
    # en desarrollo es cómodo permitir todo; en producción, setear CORS_ORIGINS.
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
# routes/alimentos.py no usa prefix para exponer exactamente:
# - GET  /alimentos
# - GET  /alimento/{codigo}
# - POST /buscar
# - POST /alimento
app.include_router(alimentos_router)

# incluir el router del asistente si se importó correctamente
if asistente_router is not None:
    app.include_router(asistente_router, prefix="")
else:
    logger.warning("Router 'asistente_ia' no incluido (import falló o no existe).")

# Handler global para RuntimeError (p. ej. errores lanzados por el repo/cliente Supabase)
@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    # Transformamos errores internos en 503 Service Unavailable
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
    """
    Healthcheck básico. Intenta solicitar 1 registro desde la tabla de alimentos
    para comprobar que la conexión a la DB (Supabase) está respondiendo.
    Devuelve 200 OK si la DB responde, o 503 si hay un error.
    """
    try:
        # Llamamos a get_all con limit=1 para validar DB.
        rows = repo_get_all(limit=1, offset=0)
        # repo_get_all devuelve lista (posiblemente vacía) o lanza RuntimeError
        return {"status": "ok", "db_rows_returned": len(rows)}
    except RuntimeError as e:
        # Devolvemos error identificable para que herramientas de monitoreo lo entiendan
        logger.exception("Healthcheck falló al consultar la DB")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "detail": "DB unreachable", "error": str(e)},
        )


# Mostrar rutas registradas al arrancar por razones de debug
@app.on_event("startup")
def log_registered_routes():
    try:
        for r in app.routes:
            methods = ",".join(getattr(r, "methods", []))
            # endpoint puede ser Callable u objeto; mostramos su nombre si existe
            endpoint_name = getattr(r.endpoint, "__name__", r.endpoint.__class__.__name__ if hasattr(r.endpoint, "__class__") else str(r.endpoint))
            logger.info("Route: %s %s -> %s", methods, r.path, endpoint_name)
    except Exception:
        logger.exception("Error listando rutas al startup")
