"""
Modelo de dominio: Partido.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass
class Partido:
    """
    Representa un enfrentamiento entre dos equipos dentro de un fixture.

    Attributes:
        id_fixture:       UUID del fixture al que pertenece.
        id_equipo_local:  UUID del equipo local.
        id_equipo_visita: UUID del equipo visitante.
        jornada:          Número de la jornada dentro del fixture.
        fecha:            Fecha programada del partido (opcional).
        jugado:           True si el partido ya fue disputado.
        id:               UUID asignado tras la persistencia.
    """
    id_fixture: UUID
    id_equipo_local: UUID
    id_equipo_visita: UUID
    jornada: int
    fecha: Optional[date] = None
    jugado: bool = False
    id: Optional[UUID] = None

    def __str__(self) -> str:
        estado = "✔ Jugado" if self.jugado else "⏳ Pendiente"
        return f"Jornada {self.jornada} | Local vs Visita | {estado}"
