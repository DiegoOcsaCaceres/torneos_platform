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

    def generar_siguiente_ronda(
        self,
        id_torneo: int,
        id_cancha: int,
        fecha_inicio: Optional[date] = None,
    ) -> dict:
        """
        Avanza el bracket de un Torneo Relámpago a la siguiente fase, tomando
        los ganadores de la última fase jugada (por marcador, o por penales
        si hubo empate).

        Returns:
            dict con:
              - 'finalizado': True si ya se determinó un campeón (no se crean
                               partidos nuevos).
              - 'campeon':    dict del equipo campeón, o None.
              - 'partidos':   lista de partidos creados para la nueva fase
                               (vacía si finalizado).

        Raises:
            FixtureError:     Si no hay bracket generado, si quedan partidos
                               pendientes en la fase actual, o si hay un
                               empate sin penales registrados.
            RepositorioError: Si falla la persistencia.
        """
        ultima_fase = self._partido_repo.obtener_ultima_fase(id_torneo)
        if ultima_fase is None:
            raise FixtureError("Este torneo no tiene un bracket generado todavía.")

        filas = self._partido_repo.listar_partidos_de_fase(id_torneo, ultima_fase)
        if not filas:
            raise FixtureError(f"No se encontraron partidos en la fase '{ultima_fase}'.")

        # Agrupar filas por id_partido, preservando el orden de aparición
        partidos_agrupados = {}
        orden_partidos = []
        for fila in filas:
            id_p = fila['id_partido']
            if id_p not in partidos_agrupados:
                partidos_agrupados[id_p] = []
                orden_partidos.append(id_p)
            partidos_agrupados[id_p].append(fila)

        ganadores = []
        for id_p in orden_partidos:
            equipos_partido = partidos_agrupados[id_p]

            if equipos_partido[0]['estado'] != 'Finalizado':
                raise FixtureError(
                    "Aún hay partidos pendientes en la fase actual. "
                    "Registra todos los resultados antes de avanzar de ronda."
                )

            if len(equipos_partido) == 1:
                # Bye: gana automáticamente, sin rival
                ganadores.append({
                    'id_equipo': equipos_partido[0]['id_equipo'],
                    'nombre_equipo': equipos_partido[0]['nombre_equipo'],
                })
                continue

            equipo_a, equipo_b = equipos_partido[0], equipos_partido[1]
            puntaje_a = equipo_a['puntaje'] or 0
            puntaje_b = equipo_b['puntaje'] or 0

            if puntaje_a > puntaje_b:
                ganador = equipo_a
            elif puntaje_b > puntaje_a:
                ganador = equipo_b
            else:
                pen_a = (equipo_a['penales_local'] if equipo_a['id_condicion'] == ID_CONDICION_LOCAL
                         else equipo_a['penales_visita'])
                pen_b = (equipo_b['penales_local'] if equipo_b['id_condicion'] == ID_CONDICION_LOCAL
                         else equipo_b['penales_visita'])

                if pen_a is None or pen_b is None:
                    raise FixtureError(
                        f"El partido entre '{equipo_a['nombre_equipo']}' y "
                        f"'{equipo_b['nombre_equipo']}' terminó empatado y no tiene "
                        "penales registrados. Registra el resultado con penales "
                        "antes de avanzar de ronda."
                    )
                if pen_a == pen_b:
                    raise FixtureError(
                        f"El partido entre '{equipo_a['nombre_equipo']}' y "
                        f"'{equipo_b['nombre_equipo']}' también quedó empatado en "
                        "penales. Corrige el resultado antes de avanzar de ronda."
                    )
                ganador = equipo_a if pen_a > pen_b else equipo_b

            ganadores.append({
                'id_equipo': ganador['id_equipo'],
                'nombre_equipo': ganador['nombre_equipo'],
            })

        if len(ganadores) == 1:
            return {'finalizado': True, 'campeon': ganadores[0], 'partidos': []}

        numero_ronda_siguiente = self._partido_repo.contar_fases_distintas(id_torneo) + 1
        nombre_fase = self._nombre_fase_siguiente(len(ganadores), numero_ronda_siguiente)

        partidos_creados = []
        i = 0
        while i < len(ganadores):
            if i + 1 < len(ganadores):
                local, visita = ganadores[i], ganadores[i + 1]
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
                    PartidoEquipo(id_partido=id_partido, id_equipo=local['id_equipo'], id_condicion=ID_CONDICION_LOCAL)
                )
                self._partido_repo.guardar_partido_equipo(
                    PartidoEquipo(id_partido=id_partido, id_equipo=visita['id_equipo'], id_condicion=ID_CONDICION_VISITANTE)
                )
                partidos_creados.append(partido_data)
            else:
                equipo_bye = ganadores[i]
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
                    PartidoEquipo(id_partido=id_partido, id_equipo=equipo_bye['id_equipo'], id_condicion=ID_CONDICION_LOCAL)
                )
                partidos_creados.append(partido_data)
            i += 2

        return {'finalizado': False, 'campeon': None, 'partidos': partidos_creados}

    @staticmethod
    def _nombre_fase_siguiente(num_ganadores: int, numero_ronda: int) -> str:
        """Determina el nombre de la siguiente fase, replicando exactamente
        la lógica de handleGenerateNextRound del frontend."""
        if num_ganadores == 2:
            return "Gran Final"
        if num_ganadores <= 4:
            return "Semifinales"
        if num_ganadores <= 8:
            return "Cuartos de Final"
        return f"Ronda {numero_ronda}"