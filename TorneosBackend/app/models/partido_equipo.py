"""
Modelo de dominio: Partido_Equipo.
Tabla intermedia que relaciona un Partido con un Equipo y su Condicion (Local/Visitante).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PartidoEquipo:
    """
    Relaciona un partido con un equipo y su condición de juego.

    Attributes:
        id_partido:        FK al partido.
        id_equipo:         FK al equipo.
        id_condicion:      FK a la condición (Local=1, Visitante=2).
        id_partido_equipo: ID serial asignado tras la persistencia.
    """
    id_partido: int
    id_equipo: int
    id_condicion: int
    id_partido_equipo: Optional[int] = None

    def __str__(self) -> str:
        return (
            f"PartidoEquipo | Partido:{self.id_partido} "
            f"Equipo:{self.id_equipo} Condicion:{self.id_condicion}"
        )
