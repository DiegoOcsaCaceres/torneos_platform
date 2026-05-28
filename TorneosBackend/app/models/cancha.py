"""
Modelo de dominio: Cancha.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Cancha:
    """
    Representa una cancha donde se disputan los partidos.

    Attributes:
        nombre_cancha: Nombre de la cancha.
        tipo:          Tipo de cancha (ej: 'Vóley', 'Fútbol').
        id_cancha:     ID serial asignado tras la persistencia.
    """
    nombre_cancha: str
    tipo: Optional[str] = None
    id_cancha: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.nombre_cancha} ({self.tipo})"
