"""
Endpoints para gestionar canciones.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, select

from musica_api.database import get_session
from musica_api.models import (
    Cancion,
    CancionCreate,
    CancionRead,
    CancionUpdate,
    Favorito,
)

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


def _obtener_cancion(session: Session, cancion_id: int) -> Cancion:
    cancion = session.get(Cancion, cancion_id)
    if cancion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Canción no encontrada")
    return cancion


@router.get("", response_model=list[CancionRead])
def listar_canciones(session: SessionDep):
    return session.exec(select(Cancion)).all()


@router.post("", response_model=CancionRead, status_code=status.HTTP_201_CREATED)
def crear_cancion(datos: CancionCreate, session: SessionDep):
    cancion = Cancion(**datos.model_dump())
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion


# IMPORTANTE: /buscar va ANTES de /{cancion_id}; si no, FastAPI intentaría
# interpretar "buscar" como un id y devolvería un error 422.
@router.get("/buscar", response_model=list[CancionRead])
def buscar_canciones(
    session: SessionDep,
    titulo: str | None = None,
    artista: str | None = None,
    genero: str | None = None,
):
    consulta = select(Cancion)
    if titulo:
        consulta = consulta.where(col(Cancion.titulo).ilike(f"%{titulo}%"))
    if artista:
        consulta = consulta.where(col(Cancion.artista).ilike(f"%{artista}%"))
    if genero:
        consulta = consulta.where(col(Cancion.genero).ilike(f"%{genero}%"))
    return session.exec(consulta).all()


@router.get("/{cancion_id}", response_model=CancionRead)
def obtener_cancion(cancion_id: int, session: SessionDep):
    return _obtener_cancion(session, cancion_id)


@router.put("/{cancion_id}", response_model=CancionRead)
def actualizar_cancion(cancion_id: int, datos: CancionUpdate, session: SessionDep):
    cancion = _obtener_cancion(session, cancion_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(cancion, campo, valor)
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion


@router.delete("/{cancion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cancion(cancion_id: int, session: SessionDep):
    cancion = _obtener_cancion(session, cancion_id)
    # Borrar primero los favoritos que apuntan a esta canción
    favoritos = session.exec(
        select(Favorito).where(Favorito.id_cancion == cancion_id)
    ).all()
    for favorito in favoritos:
        session.delete(favorito)
    session.delete(cancion)
    session.commit()
