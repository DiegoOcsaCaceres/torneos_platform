"""
Subclase concreta TorneoVoley — Avance 1.
Reglas FIVB: victoria=3 pts, derrota=0 pts. No existe empate.
El marcador representa sets ganados (máx 3 por equipo).
"""
from dataclasses import dataclass
from app.models.torneo import Torneo
from config.settings import PUNTOS_VICTORIA_VOLEY, PUNTOS_DERROTA_VOLEY

MAX_SETS: int = 3


@dataclass
class TorneoVoley(Torneo):
    """
    Torneo de voley con reglas estándar FIVB.

    Puntuación:
        - Victoria: 3 puntos
        - Derrota:  0 puntos (no existe empate en voley)
    """

    @property
    def tipo_deporte(self) -> str:
        return 'voley'

    def calcular_puntos(self, goles_favor: int, goles_contra: int) -> int:
        """Retorna los puntos según sets ganados."""
        if goles_favor > goles_contra:
            return PUNTOS_VICTORIA_VOLEY
        return PUNTOS_DERROTA_VOLEY

    def validar_resultado(self, marcador_local: int, marcador_visita: int) -> bool:
        """
        En voley el marcador son sets (0-3).
        Al menos un equipo debe llegar a 3 sets; no puede haber empate 3-3.
        """
        ambos_validos = (
            isinstance(marcador_local, int)
            and isinstance(marcador_visita, int)
            and 0 <= marcador_local <= MAX_SETS
            and 0 <= marcador_visita <= MAX_SETS
        )
        if not ambos_validos:
            return False
        hay_ganador = marcador_local == MAX_SETS or marcador_visita == MAX_SETS
        no_empate   = not (marcador_local == MAX_SETS and marcador_visita == MAX_SETS)
        return hay_ganador and no_empate
