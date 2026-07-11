"""
Servicio de generación del fixture round-robin.
Adaptado al nuevo schema: crea Partido + Partido_Equipo (Local/Visitante).
"""
import logging
import random
from datetime import date
from typing import Optional

from app.exceptions import FixtureError, RepositorioError
from app.models.partido import Partido
from app.models.partido_equipo import PartidoEquipo
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.partido_repo import PartidoRepository

logger = logging.getLogger(__name__)

ID_CONDICION_LOCAL = 1
ID_CONDICION_VISITANTE = 2


class FixtureService:
    """
    Genera el calendario round-robin para un torneo.
    Por cada enfrentamiento crea:
      - 1 fila en Partido
      - 2 filas en Partido_Equipo (una Local, una Visitante)
    """

    def __init__(
        self,
        partido_repo: PartidoRepository,
        equipo_repo: EquipoRepository,
    ) -> None:
        self._partido_repo = partido_repo
        self._equipo_repo = equipo_repo

    def generar_fixture(
        self,
        id_torneo: int,
        id_cancha: int,
        fecha_inicio: Optional[date] = None,
        regenerar: bool = False,
    ) -> list:
        """
        Genera y persiste el fixture round-robin para el torneo.

        Args:
            id_torneo:    ID del torneo.
            id_cancha:    ID de la cancha donde se jugarán los partidos.
            fecha_inicio: Fecha base opcional para los partidos.
            regenerar:    Si es True y el fixture existente no tiene partidos
                          finalizados, lo borra y genera uno nuevo desde cero.

        Returns:
            Lista de dicts con los partidos creados.

        Raises:
            FixtureError:     Si hay menos de 2 equipos, si ya existe un
                               fixture y no se pidió regenerar, o si ya hay
                               partidos finalizados (no se puede regenerar).
            RepositorioError: Si falla la persistencia.
        """
        equipos = self._equipo_repo.listar_por_torneo(id_torneo)
        if len(equipos) < 2:
            raise FixtureError(
                "Se necesitan al menos 2 equipos para generar el fixture."
            )

        partidos_existentes = self._partido_repo.contar_por_torneo(id_torneo)
        if partidos_existentes > 0:
            if not regenerar:
                raise FixtureError(
                    "Este torneo ya tiene un fixture generado. "
                    "Vuelve a intentarlo con regenerar=true si quieres reemplazarlo."
                )
            if self._partido_repo.existe_partido_finalizado(id_torneo):
                raise FixtureError(
                    "No se puede regenerar el fixture: ya hay partidos con "
                    "resultados registrados en este torneo."
                )
            self._partido_repo.eliminar_por_torneo(id_torneo)

        ids_equipos = [e['id_equipo'] for e in equipos]
        rondas = self._round_robin(ids_equipos)

        partidos_creados = []
        for emparejamientos in rondas:
            for id_local, id_visita in emparejamientos:
                # Crear partido
                partido = Partido(
                    id_torneo=id_torneo,
                    id_cancha=id_cancha,
                    fecha=fecha_inicio,
                    estado='Pendiente',
                )
                partido_data = self._partido_repo.guardar_partido(partido)
                id_partido = partido_data['id_partido']

                # Crear Partido_Equipo local
                self._partido_repo.guardar_partido_equipo(
                    PartidoEquipo(
                        id_partido=id_partido,
                        id_equipo=id_local,
                        id_condicion=ID_CONDICION_LOCAL,
                    )
                )
                # Crear Partido_Equipo visitante
                self._partido_repo.guardar_partido_equipo(
                    PartidoEquipo(
                        id_partido=id_partido,
                        id_equipo=id_visita,
                        id_condicion=ID_CONDICION_VISITANTE,
                    )
                )
                partidos_creados.append(partido_data)

        return partidos_creados

    def ver_fixture(self, id_torneo: int) -> list:
        """Retorna todos los partidos del fixture de un torneo."""
        return self._partido_repo.listar_por_torneo(id_torneo)

    def generar_bracket_inicial(
        self,
        id_torneo: int,
        id_cancha: int,
        fecha_inicio: Optional[date] = None,
    ) -> list:
        """
        Genera la Ronda 1 de un Torneo Relámpago (eliminación directa):
        mezcla los equipos al azar y los empareja de a pares. Si el número
        de equipos es impar, el último equipo pasa automáticamente a la
        siguiente ronda ("bye"), registrado como un partido ya Finalizado
        con un solo equipo (sin rival).

        Args:
            id_torneo:    ID del torneo.
            id_cancha:    ID de la cancha donde se jugarán los partidos.
            fecha_inicio: Fecha base opcional para los partidos.

        Returns:
            Lista de dicts con los partidos creados (incluye los "bye").

        Raises:
            FixtureError:     Si hay menos de 2 equipos, o si el torneo ya
                               tiene partidos generados.
            RepositorioError: Si falla la persistencia.
        """
        equipos = self._equipo_repo.listar_por_torneo(id_torneo)
        if len(equipos) < 2:
            raise FixtureError(
                "Se necesitan al menos 2 equipos para generar el bracket."
            )

        partidos_existentes = self._partido_repo.contar_por_torneo(id_torneo)
        if partidos_existentes > 0:
            raise FixtureError(
                "Este torneo ya tiene un bracket generado."
            )

        equipos_mezclados = equipos[:]
        random.shuffle(equipos_mezclados)
        nombre_fase = self._nombre_fase(len(equipos_mezclados))

        partidos_creados = []
        i = 0
        while i < len(equipos_mezclados):
            if i + 1 < len(equipos_mezclados):
                # Enfrentamiento normal
                local = equipos_mezclados[i]
                visita = equipos_mezclados[i + 1]
                partido = Partido(
                    id_torneo=id_torneo,
                    id_cancha=id_cancha,
                    fecha=fecha_inicio,
                    estado='Pendiente',
                    fase=nombre_fase,
                )
                partido_data = self._partido_repo.guardar_partido(partido)
                id_partido = partido_data['id_partido']
                self._partido_repo.guardar_partido_equipo(
                    PartidoEquipo(
                        id_partido=id_partido,
                        id_equipo=local['id_equipo'],
                        id_condicion=ID_CONDICION_LOCAL,
                    )
                )
                self._partido_repo.guardar_partido_equipo(
                    PartidoEquipo(
                        id_partido=id_partido,
                        id_equipo=visita['id_equipo'],
                        id_condicion=ID_CONDICION_VISITANTE,
                    )
                )
                partidos_creados.append(partido_data)
            else:
                # Bye: el equipo que sobra avanza automáticamente, sin rival
                equipo_bye = equipos_mezclados[i]
                partido = Partido(
                    id_torneo=id_torneo,
                    id_cancha=id_cancha,
                    fecha=fecha_inicio,
                    estado='Finalizado',
                    fase=nombre_fase,
                )
                partido_data = self._partido_repo.guardar_partido(partido)
                id_partido = partido_data['id_partido']
                self._partido_repo.guardar_partido_equipo(
                    PartidoEquipo(
                        id_partido=id_partido,
                        id_equipo=equipo_bye['id_equipo'],
                        id_condicion=ID_CONDICION_LOCAL,
                    )
                )
                partidos_creados.append(partido_data)
            i += 2

        return partidos_creados

    @staticmethod
    def _nombre_fase(num_equipos: int) -> str:
        """Determina el nombre de la fase según cuántos equipos compiten en ella."""
        if 8 < num_equipos <= 16:
            return "Octavos de Final"
        if 4 < num_equipos <= 8:
            return "Cuartos de Final"
        if 2 < num_equipos <= 4:
            return "Semifinales"
        if num_equipos == 2:
            return "Gran Final"
        return "Ronda 1"

    @staticmethod
    def _round_robin(ids: list) -> list:
        """
        Genera rondas round-robin. Con N impar agrega un 'bye' (None).
        Omite emparejamientos con None del resultado final.
        """
        equipos = ids[:]
        if len(equipos) % 2 != 0:
            equipos.append(None)

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
            equipos = [equipos[0]] + [equipos[-1]] + equipos[1:-1]

        return rondas
