"""
Endpoints para gestionar favoritos.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from musica_api.database import get_session
from musica_api.models import (
    Cancion,
    Favorito,
    FavoritoCreate,
    FavoritoRead,
    Usuario,
)

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


def marcar_favorito(session: Session, id_usuario: int, id_cancion: int) -> Favorito:
    """Crea un favorito verificando que existan el usuario y la canción."""
    if session.get(Usuario, id_usuario) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if session.get(Cancion, id_cancion) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Canción no encontrada")

    existente = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == id_usuario,
            Favorito.id_cancion == id_cancion,
        )
    ).first()
    if existente:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "La canción ya está marcada como favorita por este usuario",
        )

    favorito = Favorito(id_usuario=id_usuario, id_cancion=id_cancion)
    session.add(favorito)
    session.commit()
    session.refresh(favorito)
    return favorito


@router.get("", response_model=list[FavoritoRead])
def listar_favoritos(session: SessionDep):
    return session.exec(select(Favorito)).all()


@router.post("", response_model=FavoritoRead, status_code=status.HTTP_201_CREATED)
def crear_favorito(datos: FavoritoCreate, session: SessionDep):
    return marcar_favorito(session, datos.id_usuario, datos.id_cancion)


@router.get("/{favorito_id}", response_model=FavoritoRead)
def obtener_favorito(favorito_id: int, session: SessionDep):
    favorito = session.get(Favorito, favorito_id)
    if favorito is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorito no encontrado")
    return favorito


@router.delete("/{favorito_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_favorito(favorito_id: int, session: SessionDep):
    favorito = session.get(Favorito, favorito_id)
    if favorito is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorito no encontrado")
    session.delete(favorito)
    session.commit()
