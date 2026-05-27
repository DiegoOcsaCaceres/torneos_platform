"""
Modelo de dominio: Jugador.
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Jugador:
    """
    Representa un jugador perteneciente a un equipo.

    Attributes:
        id_equipo: UUID del equipo al que pertenece.
        nombre:    Nombre completo del jugador.
        numero:    Número de camiseta (1-99).
        posicion:  Posición en el campo/cancha.
        edad:      Edad del jugador (10-60).
        activo:    Indica si el jugador está habilitado.
        id:        UUID asignado tras la persistencia.
    """
    id_equipo: UUID
    nombre: str
    numero: int
    posicion: str
    edad: int
    activo: bool = True
    id: Optional[UUID] = field_default = None

    def __str__(self) -> str:
        return f"#{self.numero} {self.nombre} ({self.posicion}) - {self.edad} años"
