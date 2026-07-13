"""
Modelo de dominio: Partido.
Adaptado al nuevo schema: id_cancha, id_torneo, hora, estado, fase.
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
        fase:       Ronda del partido en Torneo Relámpago (ej: 'Cuartos de Final',
                    'Semifinal', 'Gran Final'). None en torneos tipo Liga.
        id_partido: ID serial asignado tras la persistencia.
    """
    id_torneo: int
    id_cancha: int
    fecha: Optional[date] = None
    hora: Optional[time] = None
    estado: str = 'Pendiente'
    fase: Optional[str] = None
    id_partido: Optional[int] = None

    def __str__(self) -> str:
        fase_str = f" | {self.fase}" if self.fase else ""
        return f"Partido #{self.id_partido} | {self.fecha} {self.hora} | {self.estado}{fase_str}"