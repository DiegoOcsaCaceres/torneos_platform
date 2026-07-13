"""
Subclase concreta TorneoVoley.
Victoria=3 pts, derrota=0 pts. No hay empate en voley.
"""
from dataclasses import dataclass
from app.models.torneo import Torneo
from config.settings import PUNTOS_VICTORIA_VOLEY, PUNTOS_DERROTA_VOLEY

MAX_SETS: int = 3


@dataclass
class TorneoVoley(Torneo):
    """Torneo de voley con reglas estándar FIVB."""

    @property
    def tipo_deporte(self) -> str:
        return 'voley'

    def calcular_puntos(self, marcador_favor: int, marcador_contra: int) -> int:
        if marcador_favor > marcador_contra:
            return PUNTOS_VICTORIA_VOLEY
        return PUNTOS_DERROTA_VOLEY

    def validar_resultado(self, marcador_local: int, marcador_visita: int) -> bool:
        ambos_validos = (
            isinstance(marcador_local, int)
            and isinstance(marcador_visita, int)
            and 0 <= marcador_local <= MAX_SETS
            and 0 <= marcador_visita <= MAX_SETS
        )
        if not ambos_validos:
            return False
        hay_ganador = marcador_local == MAX_SETS or marcador_visita == MAX_SETS
        no_empate = not (marcador_local == MAX_SETS and marcador_visita == MAX_SETS)
        return hay_ganador and no_empate
