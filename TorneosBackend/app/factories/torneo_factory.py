"""
Factory Method para crear instancias de Torneo según el tipo de deporte.
Adaptado al nuevo schema: recibe id_deporte (INT) y nombre_torneo.
"""
from datetime import date

from app.models.torneo_futbol import TorneoFutbol
from app.models.torneo_voley import TorneoVoley
from config.settings import DEPORTES_VALIDOS, MIN_EQUIPOS, MAX_EQUIPOS_FUTBOL, MAX_EQUIPOS_VOLEY


class TorneoFactory:
    """Crea el objeto Torneo correcto según el tipo de deporte."""

    @staticmethod
    def crear(
        tipo_deporte: str,
        nombre_torneo: str,
        numero_equipos: int,
        fecha_inicio: date,
        id_deporte: int,
        formato: str = 'liga',
    ):
        """
        Valida los parámetros y retorna una instancia de TorneoFutbol o TorneoVoley.

        Args:
            tipo_deporte:   'futbol' o 'voley'.
            nombre_torneo:  Nombre del torneo.
            numero_equipos: Número máximo de equipos.
            fecha_inicio:   Fecha de inicio.
            id_deporte:     FK al deporte en la BD.

        Returns:
            TorneoFutbol | TorneoVoley

        Raises:
            ValueError: Si los parámetros son inválidos.
        """
        tipo = tipo_deporte.strip().lower()
        if tipo not in DEPORTES_VALIDOS:
            raise ValueError(
                f"Tipo de deporte inválido: '{tipo_deporte}'. "
                f"Opciones: {sorted(DEPORTES_VALIDOS)}"
            )

        nombre_torneo = nombre_torneo.strip()
        if not nombre_torneo or len(nombre_torneo) > 100:
            raise ValueError("El nombre del torneo debe tener entre 1 y 100 caracteres.")

        max_e = MAX_EQUIPOS_FUTBOL if tipo == 'futbol' else MAX_EQUIPOS_VOLEY
        if not (MIN_EQUIPOS <= numero_equipos <= max_e):
            raise ValueError(
                f"El número de equipos debe estar entre {MIN_EQUIPOS} y {max_e}."
            )

        if formato not in ('liga', 'eliminacion_directa'):
            raise ValueError(
                f"Formato de torneo inválido: '{formato}'. "
                "Opciones: 'liga' o 'eliminacion_directa'."
            )

        kwargs = dict(
            nombre_torneo=nombre_torneo,
            fecha_inicio=fecha_inicio,
            numero_equipos=numero_equipos,
            id_deporte=id_deporte,
            formato=formato,
        )

        if tipo == 'futbol':
            return TorneoFutbol(**kwargs)
        return TorneoVoley(**kwargs)
