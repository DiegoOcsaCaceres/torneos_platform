"""
Modelo de dominio: Resultado.
Adaptado al nuevo schema: puntaje por id_partido_equipo, con soporte
opcional de penales para Torneo Relámpago (eliminación directa).
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
        penales:           Goles de penales, solo si el partido se definió
                            por tanda de penales (Torneo Relámpago). None
                            en cualquier otro caso, incluyendo Liga.
        id_resultado:      ID serial asignado tras la persistencia.
    """
    puntaje: int
    id_partido_equipo: int
    penales: Optional[int] = None
    id_resultado: Optional[int] = None

    def __str__(self) -> str:
        penales_str = f" ({self.penales} en penales)" if self.penales is not None else ""
        return f"Resultado: {self.puntaje} pts{penales_str} (PartidoEquipo #{self.id_partido_equipo})"