"""
Controller de Torneos.
Adaptado al nuevo schema: usa nombre_torneo, numero_equipos, id_deporte.
"""
from datetime import datetime
from typing import Optional

from app.exceptions import TorneoNoEncontradoError, RepositorioError
from app.services.torneo_service import TorneoService


class TorneoController:
    """Coordina las acciones sobre torneos entre Vista y Servicio."""

    def __init__(self, torneo_service: TorneoService) -> None:
        self._service = torneo_service

    def crear(
        self,
        tipo_deporte: str,
        nombre_torneo: str,
        numero_equipos: int,
        fecha_inicio_str: str,
        id_deporte: int,
    ) -> tuple[bool, str, Optional[dict]]:
        """Crea un nuevo torneo."""
        try:
            fecha = datetime.strptime(fecha_inicio_str.strip(), '%Y-%m-%d').date()
            torneo = self._service.crear_torneo(
                tipo_deporte=tipo_deporte,
                nombre_torneo=nombre_torneo,
                numero_equipos=int(numero_equipos),
                fecha_inicio=fecha,
                id_deporte=int(id_deporte),
            )
            return True, f"Torneo '{torneo['nombre_torneo']}' creado exitosamente.", torneo
        except (ValueError, TypeError) as exc:
            return False, f"Datos inválidos: {exc}", None
        except RepositorioError as exc:
            return False, f"Error de base de datos: {exc}", None

    def listar(self) -> tuple[bool, str, list]:
        """Lista todos los torneos registrados."""
        try:
            torneos = self._service.listar_torneos()
            if not torneos:
                return True, "No hay torneos registrados aún.", []
            return True, f"{len(torneos)} torneo(s) encontrado(s).", torneos
        except RepositorioError as exc:
            return False, f"Error al obtener torneos: {exc}", []

    def listar_deportes(self) -> tuple[bool, str, list]:
        """Lista todos los deportes disponibles."""
        try:
            deportes = self._service.listar_deportes()
            return True, f"{len(deportes)} deporte(s) disponible(s).", deportes
        except RepositorioError as exc:
            return False, f"Error al obtener deportes: {exc}", []

    def obtener(self, id_torneo: int) -> tuple[bool, str, Optional[dict]]:
        """Obtiene los detalles de un torneo por su ID."""
        try:
            torneo = self._service.obtener_torneo(int(id_torneo))
            return True, "Torneo encontrado.", torneo
        except TorneoNoEncontradoError as exc:
            return False, str(exc), None
        except (ValueError, RepositorioError) as exc:
            return False, f"Error: {exc}", None
