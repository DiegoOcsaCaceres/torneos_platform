"""
Modelo de dominio: Resultado.
Adaptado al nuevo schema: puntaje por id_partido_equipo.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Resultado:
    """
    Registra el puntaje de un equipo en un partido.

    Attributes:
        puntaje:           Goles/sets anotados por el equipo.
        id_partido_equipo: FK a la relación Partido_Equipo.
        id_resultado:      ID serial asignado tras la persistencia.
    """
    puntaje: int
    id_partido_equipo: int
    id_resultado: Optional[int] = None

    def __str__(self) -> str:
        return f"Resultado: {self.puntaje} pts (PartidoEquipo #{self.id_partido_equipo})"
