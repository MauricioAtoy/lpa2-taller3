"""
Endpoints para gestionar usuarios y sus favoritos.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from musica_api.database import get_session
from musica_api.models import (
    Favorito,
    FavoritoRead,
    Usuario,
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
)
from musica_api.routers.favoritos import marcar_favorito

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


def _obtener_usuario(session: Session, usuario_id: int) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return usuario


def _correo_en_uso(session: Session, correo: str, excepto_id: int | None = None):
    consulta = select(Usuario).where(Usuario.correo == correo)
    existente = session.exec(consulta).first()
    return existente is not None and existente.id != excepto_id


@router.get("", response_model=list[UsuarioRead])
def listar_usuarios(session: SessionDep):
    return session.exec(select(Usuario)).all()


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate, session: SessionDep):
    if _correo_en_uso(session, datos.correo):
        raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está registrado")
    usuario = Usuario(nombre=datos.nombre, correo=datos.correo)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int, session: SessionDep):
    return _obtener_usuario(session, usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate, session: SessionDep):
    usuario = _obtener_usuario(session, usuario_id)
    cambios = datos.model_dump(exclude_unset=True)

    nuevo_correo = cambios.get("correo")
    if nuevo_correo and _correo_en_uso(session, nuevo_correo, usuario_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está registrado")

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, session: SessionDep):
    usuario = _obtener_usuario(session, usuario_id)
    # Borrar primero sus favoritos para no dejar registros huérfanos
    favoritos = session.exec(
        select(Favorito).where(Favorito.id_usuario == usuario_id)
    ).all()
    for favorito in favoritos:
        session.delete(favorito)
    session.delete(usuario)
    session.commit()


# -----------------------------------------------------------------------------
# Favoritos de un usuario
# -----------------------------------------------------------------------------


@router.get("/{usuario_id}/favoritos", response_model=list[FavoritoRead])
def listar_favoritos_usuario(usuario_id: int, session: SessionDep):
    _obtener_usuario(session, usuario_id)
    return session.exec(select(Favorito).where(Favorito.id_usuario == usuario_id)).all()


@router.post(
    "/{usuario_id}/favoritos/{cancion_id}",
    response_model=FavoritoRead,
    status_code=status.HTTP_201_CREATED,
)
def marcar_favorito_usuario(usuario_id: int, cancion_id: int, session: SessionDep):
    return marcar_favorito(session, usuario_id, cancion_id)


@router.delete(
    "/{usuario_id}/favoritos/{cancion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_favorito_usuario(usuario_id: int, cancion_id: int, session: SessionDep):
    favorito = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == usuario_id,
            Favorito.id_cancion == cancion_id,
        )
    ).first()
    if favorito is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorito no encontrado")
    session.delete(favorito)
    session.commit()
