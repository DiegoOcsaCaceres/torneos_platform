"""
Clase abstracta base Torneo (ABC).
Adaptada al nuevo schema: usa id_deporte (INT) en lugar de tipo_deporte (str).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Torneo(ABC):
    """
    Entidad abstracta que representa un torneo deportivo.

    Attributes:
        nombre_torneo:  Nombre descriptivo del torneo.
        fecha_inicio:   Fecha de inicio del torneo.
        numero_equipos: Límite de equipos participantes.
        id_deporte:     FK al deporte asociado.
        id_torneo:      ID serial asignado tras la persistencia.
        jugadores_por_equipo: Cantidad de jugadores requerida por equipo.
        id_usuario:     FK a la cuenta (Usuario) dueña del torneo.
    """
    nombre_torneo: str
    fecha_inicio: date
    numero_equipos: int
    id_deporte: int
    id_torneo: Optional[int] = field(default=None)
    formato: str = 'liga'
    jugadores_por_equipo: int = 5
    id_usuario: Optional[int] = field(default=None)

    @property
    @abstractmethod
    def tipo_deporte(self) -> str:
        """Retorna el identificador de la disciplina: 'futbol' o 'voley'."""

    @abstractmethod
    def calcular_puntos(self, marcador_favor: int, marcador_contra: int) -> int:
        """Calcula los puntos obtenidos según el resultado."""

    @abstractmethod
    def validar_resultado(self, marcador_local: int, marcador_visita: int) -> bool:
        """Verifica que el marcador cumple las reglas de la disciplina."""

    def __str__(self) -> str:
        return (
            f"[{self.tipo_deporte.upper()}] {self.nombre_torneo} "
            f"| Equipos: {self.numero_equipos}"
        )
