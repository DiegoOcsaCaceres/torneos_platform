"""
Modelo de dominio: Resultado.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Resultado:
    """
    Registra el marcador final de un partido disputado.

    Attributes:
        id_partido:      UUID del partido al que pertenece.
        marcador_local:  Tantos/sets del equipo local.
        marcador_visita: Tantos/sets del equipo visitante.
        es_valido:       Indica si el resultado fue validado correctamente.
        fecha_registro:  Timestamp de registro del resultado.
        id:              UUID asignado tras la persistencia.
    """
    id_partido: UUID
    marcador_local: int
    marcador_visita: int
    es_valido: bool = True
    fecha_registro: Optional[datetime] = None
    id: Optional[UUID] = None

    def __str__(self) -> str:
        return f"{self.marcador_local} - {self.marcador_visita}"
