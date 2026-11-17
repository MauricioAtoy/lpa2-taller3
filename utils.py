"""
Módulo de utilidades para la aplicación.
Contiene funciones auxiliares utilizadas en diferentes partes de la aplicación.
"""

import re
import unicodedata
from datetime import datetime


def validar_correo(correo):
    """
    Valida que un correo electrónico tenga un formato válido.

    Args:
        correo (str): Correo electrónico a validar

    Returns:
        bool: True si el correo es válido, False en caso contrario
    """
    # crear la expresión regular para validar el correo
    patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
    return bool(re.match(patron, correo))


def formatear_duracion(segundos):
    """
    Convierte una duración en segundos a formato mm:ss.

    Args:
        segundos (int): Duración en segundos

    Returns:
        str: Duración formateada como mm:ss
    """
    # pendiente de implementar
    segundos = int(segundos)
    if segundos < 0:
        raise ValueError("La duración no puede ser negativa")
    minutos, resto = divmod(segundos, 60)
    return f"{minutos:02d}:{resto:02d}"


def generar_slug(texto):
    """
    Genera un slug a partir de un texto.
    Un slug es una versión de texto amigable para URLs.

    Args:
        texto (str): Texto a convertir en slug

    Returns:
        str: Slug generado
    """
    # Convertir a minúsculas
    slug = texto.lower()

    # Quitar tildes (canción -> cancion) para no perder letras en el paso siguiente
    slug = unicodedata.normalize("NFKD", slug)
    slug = "".join(c for c in slug if not unicodedata.combining(c))

    # Reemplazar espacios con guiones
    slug = re.sub(r"\s+", "-", slug)

    # Eliminar caracteres no alfanuméricos (excepto guiones)
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Reemplazar múltiples guiones con uno solo
    slug = re.sub(r"-{2,}", "-", slug)

    # Eliminar guiones al inicio y final
    slug = slug.strip("-")

    return slug


def obtener_año_actual():
    """
    Obtiene el año actual.

    Returns:
        int: Año actual
    """
    # pendiente por implementar
    return datetime.now().year


def validar_año(año):
    """
    Valida que un año sea válido (no futuro y no muy antiguo).

    Args:
        año (int): Año a validar

    Returns:
        bool: True si el año es válido, False en caso contrario
    """
    año_actual = obtener_año_actual()
    return 1900 <= año <= año_actual
