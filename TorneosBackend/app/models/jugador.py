"""
Modelo de dominio: Jugador.
Adaptado al nuevo schema: apellido_paterno, apellido_materno, DNI.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Jugador:
    """
    Representa un jugador perteneciente a un equipo.

    Attributes:
        nombre_jugador:   Nombre del jugador.
        apellido_paterno: Apellido paterno.
        apellido_materno: Apellido materno.
        DNI:              Documento de identidad (único).
        id_equipo:        FK al equipo al que pertenece.
        id_jugador:       ID serial asignado tras la persistencia.
    """
    nombre_jugador: str
    apellido_paterno: str
    apellido_materno: str
    DNI: str
    id_equipo: int
    id_jugador: Optional[int] = None

    def nombre_completo(self) -> str:
        return f"{self.nombre_jugador} {self.apellido_paterno} {self.apellido_materno}"

    def __str__(self) -> str:
        return f"{self.nombre_completo()} | DNI: {self.DNI}"
