"""
Factory Method para crear instancias de Torneo según el tipo de deporte.
Adaptado al nuevo schema: recibe id_deporte (INT) y nombre_torneo.
"""
from datetime import date

from app.models.torneo_futbol import TorneoFutbol
from app.models.torneo_voley import TorneoVoley
from config.settings import (
    DEPORTES_VALIDOS,
    MIN_EQUIPOS,
    MAX_EQUIPOS_FUTBOL,
    MAX_EQUIPOS_VOLEY,
    MIN_JUGADORES_POR_EQUIPO_FUTBOL,
    MIN_JUGADORES_POR_EQUIPO_VOLEY,
    MAX_JUGADORES_POR_EQUIPO,
)


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
        jugadores_por_equipo: int = 5,
        id_usuario: int = None,
    ):
        """
        Valida los parámetros y retorna una instancia de TorneoFutbol o TorneoVoley.

        Args:
            tipo_deporte:   'futbol' o 'voley'.
            nombre_torneo:  Nombre del torneo.
            numero_equipos: Número máximo de equipos.
            fecha_inicio:   Fecha de inicio.
            id_deporte:     FK al deporte en la BD.
            jugadores_por_equipo: Cantidad de jugadores requerida por equipo.
            id_usuario:     FK a la cuenta dueña del torneo.

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

        min_jugadores = (
            MIN_JUGADORES_POR_EQUIPO_FUTBOL if tipo == 'futbol'
            else MIN_JUGADORES_POR_EQUIPO_VOLEY
        )
        if not (min_jugadores <= jugadores_por_equipo <= MAX_JUGADORES_POR_EQUIPO):
            raise ValueError(
                f"Para {tipo}, el número de jugadores por equipo debe estar entre "
                f"{min_jugadores} y {MAX_JUGADORES_POR_EQUIPO}."
            )

        kwargs = dict(
            nombre_torneo=nombre_torneo,
            fecha_inicio=fecha_inicio,
            numero_equipos=numero_equipos,
            id_deporte=id_deporte,
            formato=formato,
            jugadores_por_equipo=jugadores_por_equipo,
            id_usuario=id_usuario,
        )

        if tipo == 'futbol':
            return TorneoFutbol(**kwargs)
        return TorneoVoley(**kwargs)
