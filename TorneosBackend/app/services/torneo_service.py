"""
Servicio de lógica de negocio para la creación y gestión de torneos.
"""
from datetime import date

from app.exceptions import TorneoNoEncontradoError
from app.factories.torneo_factory import TorneoFactory
from app.repositories.torneo_repo import TorneoRepository


class TorneoService:
    """
    Orquesta la creación, consulta y cambio de estado de torneos.
    Nunca accede a Supabase directamente; delega en TorneoRepository.
    """

    def __init__(self, torneo_repo: TorneoRepository) -> None:
        self._torneo_repo = torneo_repo

    def crear_torneo(
        self,
        tipo_deporte: str,
        nombre: str,
        max_equipos: int,
        fecha_inicio: date,
    ) -> dict:
        """
        Valida los parámetros, crea el objeto Torneo con Factory y lo persiste.

        Returns:
            dict con los datos del torneo creado.

        Raises:
            ValueError:      Si los parámetros son inválidos.
            RepositorioError: Si falla la persistencia.
        """
        torneo = TorneoFactory.crear(
            tipo_deporte=tipo_deporte,
            nombre=nombre,
            max_equipos=max_equipos,
            fecha_inicio=fecha_inicio,
        )
        return self._torneo_repo.guardar(torneo)

    def listar_torneos(self) -> list:
        """Retorna todos los torneos registrados."""
        return self._torneo_repo.listar()

    def obtener_torneo(self, id_torneo: str) -> dict:
        """
        Busca un torneo por su ID.

        Raises:
            TorneoNoEncontradoError: Si no existe.
        """
        from uuid import UUID
        torneo = self._torneo_repo.obtener_por_id(UUID(id_torneo))
        if not torneo:
            raise TorneoNoEncontradoError(f"No se encontró el torneo con ID: {id_torneo}")
        return torneo

    def iniciar_torneo(self, id_torneo: str) -> dict:
        """Cambia el estado del torneo a 'en_curso'."""
        torneo = self.obtener_torneo(id_torneo)
        if torneo['estado'] != 'pendiente':
            raise ValueError(
                f"Solo se puede iniciar un torneo en estado 'pendiente'. "
                f"Estado actual: '{torneo['estado']}'."
            )
        from uuid import UUID
        return self._torneo_repo.actualizar_estado(UUID(id_torneo), 'en_curso')

    def finalizar_torneo(self, id_torneo: str) -> dict:
        """Cambia el estado del torneo a 'finalizado'."""
        torneo = self.obtener_torneo(id_torneo)
        if torneo['estado'] != 'en_curso':
            raise ValueError(
                f"Solo se puede finalizar un torneo 'en_curso'. "
                f"Estado actual: '{torneo['estado']}'."
            )
        from uuid import UUID
        return self._torneo_repo.actualizar_estado(UUID(id_torneo), 'finalizado')
