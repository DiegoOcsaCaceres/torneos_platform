"""
Servicio de generación del fixture round-robin (RF-05).
"""
import logging
from uuid import UUID

from app.exceptions import FixtureError, RepositorioError
from app.models.fixture import Fixture
from app.models.partido import Partido
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.partido_repo import PartidoRepository

logger = logging.getLogger(__name__)


class FixtureService:
    """
    Genera el calendario round-robin para un torneo.

    Algoritmo:
        - Con N equipos pares → N-1 jornadas, N/2 partidos por jornada.
        - Con N equipos impares → se agrega un "bye" (descanso) y se aplica
          el mismo algoritmo con N+1 equipos.
    """

    def __init__(
        self,
        partido_repo: PartidoRepository,
        equipo_repo: EquipoRepository,
    ) -> None:
        self._partido_repo = partido_repo
        self._equipo_repo = equipo_repo

    def generar_fixture(self, id_torneo: UUID) -> dict:
        """
        Genera y persiste el fixture round-robin para el torneo.

        Args:
            id_torneo: UUID del torneo para el que se genera el fixture.

        Returns:
            dict con los datos del fixture creado.

        Raises:
            FixtureError:     Si el fixture ya existe o hay menos de 2 equipos.
            RepositorioError: Si falla la persistencia.
        """
        # 1. Verificar que no existe fixture previo
        if self._partido_repo.existe_fixture(id_torneo):
            raise FixtureError(
                "Ya existe un fixture para este torneo. "
                "No se puede regenerar sin eliminarlo primero."
            )

        # 2. Obtener equipos del torneo
        equipos = self._equipo_repo.listar_por_torneo(id_torneo)
        if len(equipos) < 2:
            raise FixtureError(
                "Se necesitan al menos 2 equipos para generar el fixture."
            )

        # 3. Generar rondas con algoritmo round-robin
        ids_equipos = [e['id'] for e in equipos]
        rondas = self._round_robin(ids_equipos)

        total_jornadas = len(rondas)
        fixture = Fixture(id_torneo=id_torneo, total_jornadas=total_jornadas)

        # 4. Persistir fixture
        fixture_data = self._partido_repo.guardar_fixture(fixture)
        id_fixture = UUID(fixture_data['id'])

        # 5. Construir y persistir partidos
        partidos: list[Partido] = []
        for num_jornada, emparejamientos in enumerate(rondas, start=1):
            for local_id, visita_id in emparejamientos:
                partidos.append(
                    Partido(
                        id_fixture=id_fixture,
                        id_equipo_local=UUID(local_id),
                        id_equipo_visita=UUID(visita_id),
                        jornada=num_jornada,
                    )
                )

        self._partido_repo.guardar_partidos(id_fixture, partidos)
        return fixture_data

    # ── Algoritmo round-robin ─────────────────────────────────────────────
    @staticmethod
    def _round_robin(ids: list) -> list[list[tuple]]:
        """
        Genera rondas round-robin para una lista de IDs de equipos.
        Si el número de equipos es impar, se agrega un 'bye' (None).

        Returns:
            Lista de rondas; cada ronda es una lista de tuplas (local, visita).
            Los emparejamientos con None (bye) son omitidos del resultado.
        """
        equipos = ids[:]
        if len(equipos) % 2 != 0:
            equipos.append(None)  # bye

        n = len(equipos)
        rondas = []

        for _ in range(n - 1):
            ronda = []
            for j in range(n // 2):
                local = equipos[j]
                visita = equipos[n - 1 - j]
                if local is not None and visita is not None:
                    ronda.append((local, visita))
            rondas.append(ronda)
            # Rotar: fijar el primero, rotar el resto
            equipos = [equipos[0]] + [equipos[-1]] + equipos[1:-1]

        return rondas

    def ver_fixture(self, id_torneo: UUID) -> list:
        """Retorna todos los partidos del fixture de un torneo."""
        return self._partido_repo.listar_por_torneo(id_torneo)
