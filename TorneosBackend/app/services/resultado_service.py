"""
Servicio de registro de resultados y tabla de posiciones.
Adaptado al nuevo schema: guarda puntaje por Partido_Equipo.
"""
import logging
from typing import Optional

from app.exceptions import ResultadoInvalidoError, RepositorioError
from app.factories.torneo_factory import TorneoFactory
from app.repositories.partido_repo import PartidoRepository
from app.repositories.resultado_repo import ResultadoRepository
from app.repositories.torneo_repo import TorneoRepository

logger = logging.getLogger(__name__)


class ResultadoService:
    """
    Registra resultados y consulta la tabla de posiciones.
    """

    def __init__(
        self,
        resultado_repo: ResultadoRepository,
        partido_repo: PartidoRepository,
        torneo_repo: TorneoRepository,
    ) -> None:
        self._resultado_repo = resultado_repo
        self._partido_repo = partido_repo
        self._torneo_repo = torneo_repo

    def registrar_resultado(
        self,
        id_partido: int,
        id_partido_equipo_local: int,
        id_partido_equipo_visita: int,
        id_torneo: int,
        puntaje_local: int,
        puntaje_visita: int,
        penales_local: Optional[int] = None,
        penales_visita: Optional[int] = None,
    ) -> dict:
        """
        Registra el resultado (puntaje) de ambos equipos en un partido.

        Args:
            id_partido:                 ID del partido.
            id_partido_equipo_local:    ID del Partido_Equipo del local.
            id_partido_equipo_visita:   ID del Partido_Equipo del visitante.
            id_torneo:                  ID del torneo (para validar reglas).
            puntaje_local:              Goles/sets del equipo local.
            puntaje_visita:             Goles/sets del equipo visitante.
            penales_local:              Goles de penales del local, solo si hubo
                                         empate en Torneo Relámpago. None en Liga.
            penales_visita:             Goles de penales del visitante, en las
                                         mismas condiciones que penales_local.

        Returns:
            dict con los dos resultados registrados.

        Raises:
            ResultadoInvalidoError: Si el marcador viola las reglas del deporte.
            RepositorioError:       Si falla la persistencia.
        """
        try:
            # 1. Obtener tipo de deporte
            torneo = self._torneo_repo.obtener_por_id(id_torneo)
            if not torneo:
                raise ValueError(f"Torneo {id_torneo} no encontrado.")

            nombre_deporte = torneo.get('nombre_deporte', '').lower()
            tipo_deporte = 'futbol' if 'f' in nombre_deporte else 'voley'

            # 2. Validar marcador según reglas del deporte
            torneo_obj = TorneoFactory.crear(
                tipo_deporte=tipo_deporte,
                nombre_torneo=torneo['nombre_torneo'],
                numero_equipos=torneo['numero_equipos'],
                fecha_inicio=torneo['fecha_inicio'],
                id_deporte=torneo['id_deporte'],
            )
            if not torneo_obj.validar_resultado(puntaje_local, puntaje_visita):
                raise ResultadoInvalidoError(
                    f"El marcador {puntaje_local}-{puntaje_visita} no es válido "
                    f"para {tipo_deporte}."
                )

            # 3. Guardar resultado del local
            res_local = self._resultado_repo.guardar(
                puntaje_local, id_partido_equipo_local, penales=penales_local, es_local=True
            )
            # 4. Guardar resultado del visitante
            res_visita = self._resultado_repo.guardar(
                puntaje_visita, id_partido_equipo_visita, penales=penales_visita, es_local=False
            )

            # 5. Marcar partido como Finalizado
            self._partido_repo.actualizar_estado(id_partido, 'Finalizado')

            return {'local': res_local, 'visitante': res_visita}

        except ResultadoInvalidoError:
            raise
        except Exception as exc:
            logger.error('ResultadoService.registrar_resultado -> %s', exc)
            raise RepositorioError(
                "Error técnico al registrar el resultado. Intente de nuevo."
            ) from exc

    def ver_marcador(self, id_partido: int) -> list:
        """Retorna los puntajes de ambos equipos en un partido."""
        return self._resultado_repo.obtener_marcador_partido(id_partido)

    def ver_tabla(self, id_torneo: int) -> list:
        """Retorna la tabla de posiciones del torneo."""
        return self._resultado_repo.obtener_tabla_posiciones(id_torneo)
