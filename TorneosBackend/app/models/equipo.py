
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Equipo:
    """
    Representa un equipo inscrito en un torneo deportivo.

    Attributes:
        nombre:    Nombre único del equipo dentro del torneo.
        deporte:   Disciplina del equipo ('futbol' o 'voley').
        id_torneo: Identificador del torneo al que pertenece.
        id:        Identificador único asignado al persistir.
    """
    nombre: str
    deporte: str
    id_torneo: str
    id: Optional[str] = field(default=None)

    def __str__(self) -> str:
        return f"{self.nombre} [{self.deporte.upper()}]"
