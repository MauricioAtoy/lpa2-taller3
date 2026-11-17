"""
Modelos de la base de datos (SQLModel) y esquemas de validación (Pydantic).
"""

from datetime import UTC, datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel, UniqueConstraint

from utils import validar_año, validar_correo


def ahora() -> datetime:
    """Fecha y hora actual con zona horaria (UTC)."""
    return datetime.now(UTC)


# =============================================================================
# USUARIO
# =============================================================================


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    correo: str = Field(unique=True, index=True)
    fecha_registro: datetime = Field(default_factory=ahora)


class UsuarioCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    correo: str

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if not validar_correo(v):
            raise ValueError("Correo electrónico inválido")
        return v


class UsuarioUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    correo: str | None = None

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if not validar_correo(v):
            raise ValueError("Correo electrónico inválido")
        return v


class UsuarioRead(SQLModel):
    id: int
    nombre: str
    correo: str
    fecha_registro: datetime


# =============================================================================
# CANCIÓN
# =============================================================================


class CancionBase(SQLModel):
    titulo: str = Field(min_length=1, max_length=200)
    artista: str = Field(min_length=1, max_length=200)
    album: str | None = Field(default=None, max_length=200)
    duracion: int = Field(gt=0, description="Duración en segundos")
    año: int
    genero: str = Field(min_length=1, max_length=100)


class Cancion(CancionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha_creacion: datetime = Field(default_factory=ahora)


class CancionCreate(CancionBase):
    @field_validator("año")
    @classmethod
    def año_valido(cls, v: int) -> int:
        if not validar_año(v):
            raise ValueError("El año debe estar entre 1900 y el año actual")
        return v


class CancionUpdate(SQLModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    artista: str | None = Field(default=None, min_length=1, max_length=200)
    album: str | None = Field(default=None, max_length=200)
    duracion: int | None = Field(default=None, gt=0)
    año: int | None = None
    genero: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("año")
    @classmethod
    def año_valido(cls, v: int | None) -> int | None:
        if v is not None and not validar_año(v):
            raise ValueError("El año debe estar entre 1900 y el año actual")
        return v


class CancionRead(CancionBase):
    id: int
    fecha_creacion: datetime


# =============================================================================
# FAVORITO
# =============================================================================


class Favorito(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("id_usuario", "id_cancion"),)

    id: int | None = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    id_cancion: int = Field(foreign_key="cancion.id")
    fecha_marcado: datetime = Field(default_factory=ahora)


class FavoritoCreate(SQLModel):
    id_usuario: int
    id_cancion: int


class FavoritoRead(SQLModel):
    id: int
    id_usuario: int
    id_cancion: int
    fecha_marcado: datetime
