"""
Modelo de dominio: Equipo.
Adaptado al nuevo schema: usa id_torneo (INT) y numero_jugadores.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Equipo:
    """
    Representa un equipo inscrito en un torneo deportivo.

    Attributes:
        nombre_equipo:    Nombre del equipo.
        numero_jugadores: Cantidad de jugadores del equipo.
        id_torneo:        FK al torneo al que pertenece.
        id_equipo:        ID serial asignado tras la persistencia.
    """
    nombre_equipo: str
    numero_jugadores: int
    id_torneo: int
    jugadores: List = field(default_factory=list)
    id_equipo: Optional[int] = field(default=None)

    def agregar_jugador(self, jugador) -> bool:
        if jugador in self.jugadores:
            return False
        self.jugadores.append(jugador)
        return True

    def obtener_plantilla(self) -> list:
        return list(self.jugadores)

    def __str__(self) -> str:
        return f"{self.nombre_equipo} | Jugadores: {self.numero_jugadores}"
