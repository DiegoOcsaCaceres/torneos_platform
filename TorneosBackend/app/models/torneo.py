"""
Clase abstracta base Torneo (ABC).
Define la interfaz común para TorneoFutbol y TorneoVoley.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass
class Torneo(ABC):
    """
    Entidad abstracta que representa un torneo deportivo.

    Attributes:
        nombre:       Nombre descriptivo del torneo.
        max_equipos:  Límite de equipos participantes (2-10).
        fecha_inicio: Fecha de inicio del torneo.
        estado:       Estado del torneo: 'pendiente', 'en_curso', 'finalizado'.
        id:           UUID asignado tras la persistencia en BD.
    """
    nombre: str
    max_equipos: int
    fecha_inicio: date
    estado: str = 'pendiente'
    id: Optional[UUID] = field(default=None)

    # ── Propiedades abstractas ────────────────────────────────────────────
    @property
    @abstractmethod
    def tipo_deporte(self) -> str:
        """Retorna el identificador de la disciplina: 'futbol' o 'voley'."""

    # ── Métodos abstractos ────────────────────────────────────────────────
    @abstractmethod
    def calcular_puntos(self, goles_favor: int, goles_contra: int) -> int:
        """
        Calcula los puntos 

        Returns: 
            Puntos obtenidos en el partido.
        """

    @abstractmethod
    def validar_resultado(self, marcador_local: int, marcador_visita: int) -> bool:
        """
        Verifica que el marcador cumple las reglas de la disciplina.

        Returns:
            True si el marcador es válido; False en caso contrario.
        """

    # ── Métodos concretos comunes ─────────────────────────────────────────
    def esta_activo(self) -> bool:
        """Indica si el torneo acepta cambios (no finalizado)."""
        return self.estado != 'finalizado'

    def iniciar(self) -> None:
        """Cambia el estado a 'en_curso'. Requiere estado 'pendiente'."""
        if self.estado != 'pendiente':
            raise ValueError(
                f"No se puede iniciar un torneo en estado '{self.estado}'."
            )
        self.estado = 'en_curso'

    def finalizar(self) -> None:
        """Cierra el torneo. Requiere estado 'en_curso'."""
        if self.estado != 'en_curso':
            raise ValueError(
                f"No se puede finalizar un torneo en estado '{self.estado}'."
            )
        self.estado = 'finalizado'

    def __str__(self) -> str:
        return (
            f"[{self.tipo_deporte.upper()}] {self.nombre} "
            f"| Equipos: {self.max_equipos} | Estado: {self.estado}"
        )
