"""
Servicio de lógica de negocio para la creación y consulta de torneos.
"""
from datetime import date

from app.exceptions import TorneoNoEncontradoError, TorneoConEquiposError
from app.repositories.equipo_repo import EquipoRepository
from app.factories.torneo_factory import TorneoFactory
from app.repositories.torneo_repo import TorneoRepository


class TorneoService:
    """
    Orquesta la creación y consulta de torneos.
    Nunca accede a la BD directamente; delega en TorneoRepository.
    """

    def __init__(
        self,
        torneo_repo: TorneoRepository,
        equipo_repo: EquipoRepository = None,
    ) -> None:
        self._torneo_repo = torneo_repo
        self._equipo_repo = equipo_repo or EquipoRepository()

    def crear_torneo(
        self,
        tipo_deporte: str,
        nombre_torneo: str,
        numero_equipos: int,
        fecha_inicio: date,
        id_deporte: int,
        formato: str = 'liga',
        jugadores_por_equipo: int = 5,
        id_usuario: int = None,
    ) -> dict:
        """
        Valida parámetros, crea el objeto Torneo con Factory y lo persiste
        asociado a la cuenta (id_usuario) que lo está creando.

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
            formato=formato,
            jugadores_por_equipo=jugadores_por_equipo,
            id_usuario=id_usuario,
        )
        return self._torneo_repo.guardar(torneo)

    def listar_torneos(self, id_usuario: int = None) -> list:
        """
        Retorna los torneos de la cuenta indicada.

        Si id_usuario es None, retorna todos los torneos (uso interno/admin);
        los endpoints públicos siempre deben pasar el id_usuario de la sesión.
        """
        return self._torneo_repo.listar(id_usuario=id_usuario)

    def listar_deportes(self) -> list:
        """Retorna todos los deportes disponibles."""
        return self._torneo_repo.listar_deportes()

    def obtener_torneo(self, id_torneo: int, id_usuario: int = None) -> dict:
        """
        Busca un torneo por su ID, verificando que pertenezca a id_usuario
        cuando se proporciona.

        Raises:
            TorneoNoEncontradoError: Si no existe o no pertenece a la cuenta.
        """
        torneo = self._torneo_repo.obtener_por_id(id_torneo, id_usuario=id_usuario)
        if not torneo:
            raise TorneoNoEncontradoError(f"No se encontró el torneo con ID: {id_torneo}")
        return torneo

    def eliminar_torneo(self, id_torneo: int, id_usuario: int = None) -> None:
        """
        Elimina un torneo, siempre que pertenezca a id_usuario (si se indica)
        y que no tenga equipos inscritos.

        Raises:
            TorneoNoEncontradoError: Si el torneo no existe o no es de la cuenta.
            TorneoConEquiposError:   Si el torneo tiene equipos inscritos.
        """
        torneo = self._torneo_repo.obtener_por_id(id_torneo, id_usuario=id_usuario)
        if not torneo:
            raise TorneoNoEncontradoError(f"No se encontró el torneo con ID: {id_torneo}")

        total_equipos = self._equipo_repo.contar_en_torneo(id_torneo)
        if total_equipos > 0:
            raise TorneoConEquiposError(
                f"No se puede eliminar el torneo '{torneo['nombre_torneo']}' "
                f"porque tiene {total_equipos} equipo(s) inscrito(s). "
                "Elimina primero los equipos."
            )

        self._torneo_repo.eliminar(id_torneo)
