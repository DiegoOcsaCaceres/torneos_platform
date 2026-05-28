"""
Subclase concreta TorneoFutbol.
Victoria=3, empate=1, derrota=0.
"""
from dataclasses import dataclass
from app.models.torneo import Torneo
from config.settings import (
    PUNTOS_VICTORIA_FUTBOL,
    PUNTOS_EMPATE_FUTBOL,
    PUNTOS_DERROTA_FUTBOL,
)


@dataclass
class TorneoFutbol(Torneo):
    """Torneo de fútbol con reglas estándar FIFA."""

    @property
    def tipo_deporte(self) -> str:
        return 'futbol'

    def calcular_puntos(self, marcador_favor: int, marcador_contra: int) -> int:
        if marcador_favor > marcador_contra:
            return PUNTOS_VICTORIA_FUTBOL
        if marcador_favor == marcador_contra:
            return PUNTOS_EMPATE_FUTBOL
        return PUNTOS_DERROTA_FUTBOL

    def validar_resultado(self, marcador_local: int, marcador_visita: int) -> bool:
        return (
            isinstance(marcador_local, int)
            and isinstance(marcador_visita, int)
            and marcador_local >= 0
            and marcador_visita >= 0
        )
