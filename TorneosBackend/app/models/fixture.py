"""
Modelo de dominio: Fixture.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID


@dataclass
class Fixture:
    """
    Calendario de partidos generado automáticamente para un torneo (round-robin).

    Attributes:
        id_torneo:      UUID del torneo al que pertenece.
        total_jornadas: Número total de jornadas en el fixture.
        partidos:       Lista de partidos generados.
        id:             UUID asignado tras la persistencia.
    """
    id_torneo: UUID
    total_jornadas: int
    partidos: List = field(default_factory=list)
    id: Optional[UUID] = None

    def __str__(self) -> str:
        return (
            f"Fixture | Torneo: {self.id_torneo} | "
            f"Jornadas: {self.total_jornadas} | Partidos: {len(self.partidos)}"
        )
