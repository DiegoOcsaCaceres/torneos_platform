"""
Controller del Fixture.
Adaptado al nuevo schema: usa id_torneo (INT) e id_cancha (INT).
"""
from datetime import datetime
from typing import Optional

from app.exceptions import FixtureError, RepositorioError
from app.services.fixture_service import FixtureService


class FixtureController:
    """Coordina la generación y consulta del fixture round-robin."""

    def __init__(self, fixture_service: FixtureService) -> None:
        self._service = fixture_service

    def generar(
        self,
        id_torneo: int,
        id_cancha: int,
        fecha_inicio_str: Optional[str] = None,
    ) -> tuple[bool, str, list]:
        """
        Genera el fixture round-robin para el torneo.

        Args:
            id_torneo:        ID del torneo.
            id_cancha:        ID de la cancha.
            fecha_inicio_str: Fecha base (YYYY-MM-DD) opcional.

        Returns:
            Tupla (éxito, mensaje, lista_partidos).
        """
        try:
            fecha = None
            if fecha_inicio_str:
                fecha = datetime.strptime(fecha_inicio_str.strip(), '%Y-%m-%d').date()
            partidos = self._service.generar_fixture(
                id_torneo=int(id_torneo),
                id_cancha=int(id_cancha),
                fecha_inicio=fecha,
            )
            return (
                True,
                f"Fixture generado: {len(partidos)} partido(s) creado(s).",
                partidos,
            )
        except FixtureError as exc:
            return False, str(exc), []
        except ValueError as exc:
            return False, f"Datos inválidos: {exc}", []
        except RepositorioError as exc:
            return False, f"Error de base de datos: {exc}", []

    def ver_fixture(self, id_torneo: int) -> tuple[bool, str, list]:
        """Consulta el calendario de partidos del torneo."""
        try:
            partidos = self._service.ver_fixture(int(id_torneo))
            if not partidos:
                return True, "No hay partidos en el fixture aún.", []
            return True, f"{len(partidos)} partido(s) en el fixture.", partidos
        except ValueError:
            return False, "ID de torneo inválido.", []
        except RepositorioError as exc:
            return False, f"Error al obtener el fixture: {exc}", []
