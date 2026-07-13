"""
Controller de Inscripción de Equipos.
Adaptado al nuevo schema: usa nombre_equipo, numero_jugadores, id_torneo (INT).
"""
from typing import Optional

from app.exceptions import EquipoDuplicadoError, RepositorioError
from app.services.inscripcion_service import InscripcionService


class InscripcionController:
    """Coordina las acciones de inscripción y consulta de equipos."""

    def __init__(self, inscripcion_service: InscripcionService) -> None:
        self._service = inscripcion_service

    def inscribir(
        self,
        nombre_equipo: str,
        numero_jugadores: int,
        id_torneo: int,
    ) -> tuple[bool, str, Optional[dict]]:
        """Inscribe un equipo en el torneo indicado."""
        try:
            equipo = self._service.inscribir_equipo(
                nombre_equipo=nombre_equipo,
                numero_jugadores=int(numero_jugadores),
                id_torneo=int(id_torneo),
            )
            return (
                True,
                f"Equipo '{equipo['nombre_equipo']}' inscrito exitosamente.",
                equipo,
            )
        except EquipoDuplicadoError as exc:
            return False, str(exc), None
        except ValueError as exc:
            return False, f"Datos inválidos: {exc}", None
        except RepositorioError as exc:
            return False, f"Error de base de datos: {exc}", None

    def listar_equipos(self, id_torneo: int) -> tuple[bool, str, list]:
        """Lista los equipos inscritos en un torneo."""
        try:
            equipos = self._service.listar_equipos(int(id_torneo))
            if not equipos:
                return True, "No hay equipos inscritos en este torneo.", []
            return True, f"{len(equipos)} equipo(s) inscrito(s).", equipos
        except ValueError:
            return False, "ID de torneo inválido.", []
        except RepositorioError as exc:
            return False, f"Error al listar equipos: {exc}", []
