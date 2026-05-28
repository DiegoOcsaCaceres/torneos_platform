"""
Modelo de dominio: Deporte.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Deporte:
    """
    Representa un deporte registrado en el sistema.

    Attributes:
        nombre_deporte: Nombre del deporte (ej: 'Fútbol', 'Vóley').
        reglas:         Descripción de las reglas del deporte.
        id_deporte:     ID serial asignado tras la persistencia.
    """
    nombre_deporte: str
    reglas: Optional[str] = None
    id_deporte: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.nombre_deporte}"
