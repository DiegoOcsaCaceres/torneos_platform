"""
Patrón Factory para instanciar objetos Torneo según el tipo de deporte.
"""
from datetime import date
from app.models.torneo import Torneo
from app.models.torneo_futbol import TorneoFutbol
from app.models.torneo_voley import TorneoVoley
from config.settings import DEPORTES_VALIDOS, MIN_EQUIPOS, MAX_EQUIPOS_FUTBOL


class TorneoFactory:
    """
    Crea instancias de Torneo según el tipo_deporte indicado.

    Uso:
        torneo = TorneoFactory.crear(
            tipo_deporte='futbol',
            nombre='Copa Lima 2025',
            max_equipos=8,
            fecha_inicio=date(2025, 6, 1),
        )
    """

    _registro: dict = {
        'futbol': TorneoFutbol,
        'voley': TorneoVoley,
    }

    @classmethod
    def crear(
        cls,
        tipo_deporte: str,
        nombre: str,
        max_equipos: int,
        fecha_inicio: date,
    ) -> Torneo:
        """
        Instancia el tipo de torneo correcto.

        Args:
            tipo_deporte: 'futbol' o 'voley'.
            nombre:       Nombre del torneo (1-100 caracteres).
            max_equipos:  Número máximo de equipos (2-20).
            fecha_inicio: Fecha de inicio del torneo.

        Returns:
            Instancia concreta de Torneo.

        Raises:
            ValueError: Si tipo_deporte no es válido o los parámetros son incorrectos.
        """
        tipo_deporte = tipo_deporte.strip().lower()
        if tipo_deporte not in DEPORTES_VALIDOS:
            raise ValueError(
                f"Tipo de deporte inválido: '{tipo_deporte}'. "
                f"Opciones disponibles: {sorted(DEPORTES_VALIDOS)}"
            )

        nombre = nombre.strip()
        if not nombre or len(nombre) > 100:
            raise ValueError("El nombre del torneo debe tener entre 1 y 100 caracteres.")

        if not (MIN_EQUIPOS <= max_equipos <= MAX_EQUIPOS_FUTBOL):
            raise ValueError(
                f"El número de equipos debe estar entre {MIN_EQUIPOS} y {MAX_EQUIPOS_FUTBOL}."
            )

        clase_torneo = cls._registro[tipo_deporte]
        return clase_torneo(
            nombre=nombre,
            max_equipos=max_equipos,
            fecha_inicio=fecha_inicio,
        )
