import logging
import platform
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from musica_api.config import get_settings
from musica_api.database import create_db_and_tables, get_session
from musica_api.routers import canciones, favoritos, usuarios

try:
    import resource  # Solo disponible en Linux/macOS (WSL incluido)
except ImportError:
    resource = None

settings = get_settings()
logger = logging.getLogger("musica_api")
logging.basicConfig(level=settings.log_level)
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Crear tablas en la base de datos
    create_db_and_tables()
    yield

    # Shutdown: Limpiar recursos si es necesario
    print("cerrando aplicación...")


# Crear la instancia de FastAPI con metadatos apropiados
# Incluir: title, description, version, contact, license_info
app = FastAPI(
    title="API de Películas",
    description="API RESTful para gestionar usuarios, películas y favoritos",
    version="1.0.0",
    lifespan=lifespan,
    # TODO: Agregar información de contacto y licencia
    contact={
        "name": "Tu Nombre",  # Ajusta con tus datos
        "email": "tu.correo@ejemplo.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# Configurar CORS para permitir solicitudes desde diferentes orígenes
# Esto es importante para desarrollo con frontend separado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duracion_ms,
    )
    return response


# Manejadores de errores personalizados
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Conflicto con los datos existentes (¿duplicado?)"},
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Error de base de datos")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno de base de datos"},
    )


# TODO: Incluir los routers de usuarios, canciones y favoritos
# Ejemplo:
# app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(canciones.router, prefix="/api/canciones", tags=["Canciones"])
app.include_router(favoritos.router, prefix="/api/favoritos", tags=["Favoritos"])


# Crear un endpoint raíz que retorne información básica de la API
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    Retorna información básica y enlaces a la documentación.
    """
    return {
        # TODO: Agregar información
        "nombre": settings.app_name,
        "version": settings.app_version,
        "entorno": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


def _memoria_mb():
    """Memoria máxima usada por el proceso en MB (None si no se puede medir)."""
    if resource is None:
        return None
    # En Linux ru_maxrss viene en KB
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)


# Crear un endpoint de health check para monitoreo
@app.get("/health", tags=["Health"])
def health_check(session: Session = Depends(get_session)):
    """
    Health check endpoint para verificar el estado de la API.
    Útil para sistemas de monitoreo y orquestación.
    """
    try:
        session.execute(text("SELECT 1"))
        base_de_datos = "connected"
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )
    return {
        "status": "healthy",
        # TODO: Agregar verificación de conexión a base de datos
        # TODO: Agregar información sobre el sistema (uptime, memoria, etc.)
        "database": base_de_datos,
        "sistema": {
            "uptime_segundos": round(time.time() - START_TIME),
            "memoria_mb": _memoria_mb(),
            "python": platform.python_version(),
            "plataforma": platform.system(),
        },
    }


# TODO: Opcional - Agregar middleware para logging de requests


# TODO: Opcional - Agregar manejadores de errores personalizados


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
