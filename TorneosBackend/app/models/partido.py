"""
Modelo de dominio: Partido.
Adaptado al nuevo schema: id_cancha, id_torneo, hora, estado.
"""
from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class Partido:
    """
    Representa un partido dentro de un torneo.

    Attributes:
        id_torneo:  FK al torneo al que pertenece.
        id_cancha:  FK a la cancha donde se juega.
        fecha:      Fecha del partido.
        hora:       Hora del partido.
        estado:     Estado del partido (ej: 'Pendiente', 'Finalizado').
        id_partido: ID serial asignado tras la persistencia.
    """
    id_torneo: int
    id_cancha: int
    fecha: Optional[date] = None
    hora: Optional[time] = None
    estado: str = 'Pendiente'
    id_partido: Optional[int] = None

    def __str__(self) -> str:
        return f"Partido #{self.id_partido} | {self.fecha} {self.hora} | {self.estado}"
