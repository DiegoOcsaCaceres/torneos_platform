"""
Modelo de dominio: Condicion (Local / Visitante).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Condicion:
    """
    Representa la condición de un equipo en un partido.

    Attributes:
        nombre_condicion: 'Local' o 'Visitante'.
        id_condicion:     ID serial asignado tras la persistencia.
    """
    nombre_condicion: str
    id_condicion: Optional[int] = None

    def __str__(self) -> str:
        return self.nombre_condicion
