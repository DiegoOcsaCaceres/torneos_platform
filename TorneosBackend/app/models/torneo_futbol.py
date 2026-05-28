"""
Subclase concreta TorneoFutbol — Avance 1.
Reglas de puntuación FIFA: victoria=3, empate=1, derrota=0.
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
    """
    Torneo de fútbol con reglas estándar FIFA.

    Puntuación:
        - Victoria: 3 puntos
        - Empate:   1 punto
        - Derrota:  0 puntos
    """

    @property
    def tipo_deporte(self) -> str:
        return 'futbol'

    def calcular_puntos(self, goles_favor: int, goles_contra: int) -> int:
        """Retorna los puntos según diferencia de goles."""
        if goles_favor > goles_contra:
            return PUNTOS_VICTORIA_FUTBOL
        if goles_favor == goles_contra:
            return PUNTOS_EMPATE_FUTBOL
        return PUNTOS_DERROTA_FUTBOL

    def validar_resultado(self, marcador_local: int, marcador_visita: int) -> bool:
        """En fútbol ambos marcadores deben ser enteros >= 0."""
        return (
            isinstance(marcador_local, int)
            and isinstance(marcador_visita, int)
            and marcador_local >= 0
            and marcador_visita >= 0
        )
