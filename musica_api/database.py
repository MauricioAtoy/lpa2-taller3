"""
Conexión a la base de datos y utilidades de sesión.
"""

from sqlmodel import Session, SQLModel, create_engine

from musica_api.config import get_settings

settings = get_settings()

# SQLite necesita este argumento para usarse con varios hilos (FastAPI)
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    """Crea las tablas en la base de datos si no existen."""
    # Importar los modelos para que SQLModel los registre antes de crear las tablas
    from musica_api import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependencia de FastAPI: entrega una sesión y la cierra al terminar."""
    with Session(engine) as session:
        yield session
