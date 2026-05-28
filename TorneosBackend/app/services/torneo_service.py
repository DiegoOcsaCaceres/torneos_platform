"""
Servicio de lógica de negocio para la creación y consulta de torneos.
"""
from datetime import date

from app.exceptions import TorneoNoEncontradoError
from app.factories.torneo_factory import TorneoFactory
from app.repositories.torneo_repo import TorneoRepository


class TorneoService:
    """
    Orquesta la creación y consulta de torneos.
    Nunca accede a la BD directamente; delega en TorneoRepository.
    """

    def __init__(self, torneo_repo: TorneoRepository) -> None:
        self._torneo_repo = torneo_repo

    def crear_torneo(
        self,
        tipo_deporte: str,
        nombre_torneo: str,
        numero_equipos: int,
        fecha_inicio: date,
        id_deporte: int,
    ) -> dict:
        """
        Valida parámetros, crea el objeto Torneo con Factory y lo persiste.

        Returns:
            dict con los datos del torneo creado.

        Raises:
            ValueError:       Si los parámetros son inválidos.
            RepositorioError: Si falla la persistencia.
        """
        torneo = TorneoFactory.crear(
            tipo_deporte=tipo_deporte,
            nombre_torneo=nombre_torneo,
            numero_equipos=numero_equipos,
            fecha_inicio=fecha_inicio,
            id_deporte=id_deporte,
        )
        return self._torneo_repo.guardar(torneo)

    def listar_torneos(self) -> list:
        """Retorna todos los torneos registrados."""
        return self._torneo_repo.listar()

    def listar_deportes(self) -> list:
        """Retorna todos los deportes disponibles."""
        return self._torneo_repo.listar_deportes()

    def obtener_torneo(self, id_torneo: int) -> dict:
        """
        Busca un torneo por su ID.

        Raises:
            TorneoNoEncontradoError: Si no existe.
        """
        torneo = self._torneo_repo.obtener_por_id(id_torneo)
        if not torneo:
            raise TorneoNoEncontradoError(f"No se encontró el torneo con ID: {id_torneo}")
        return torneo
