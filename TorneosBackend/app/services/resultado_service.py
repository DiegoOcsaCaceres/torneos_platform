"""
Servicio de registro de resultados y actualización de tabla de posiciones (RF-06, RF-07, RF-08).
"""
import logging
from uuid import UUID

from app.exceptions import ResultadoInvalidoError, RepositorioError
from app.repositories.resultado_repo import ResultadoRepository
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.torneo_repo import TorneoRepository
from app.factories.torneo_factory import TorneoFactory

logger = logging.getLogger(__name__)

# Mapa de reglas de puntuación por deporte
_PUNTOS = {
    'futbol': {'victoria': 3, 'empate': 1, 'derrota': 0},
    'voley':  {'victoria': 3, 'empate': 0, 'derrota': 0},
}


class ResultadoService:
    """
    Registra resultados, valida reglas del deporte y actualiza la tabla (RF-06–RF-09).
    """

    def __init__(
        self,
        resultado_repo: ResultadoRepository,
        equipo_repo: EquipoRepository,
        torneo_repo: TorneoRepository,
    ) -> None:
        self._resultado_repo = resultado_repo
        self._equipo_repo = equipo_repo
        self._torneo_repo = torneo_repo

    def registrar_resultado(
        self,
        id_partido: UUID,
        id_equipo_local: UUID,
        id_equipo_visita: UUID,
        id_torneo: UUID,
        marcador_local: int,
        marcador_visita: int,
    ) -> dict:
        """
        Registra el resultado de un partido con validación de reglas (RF-07).

        Args:
            id_partido:       UUID del partido.
            id_equipo_local:  UUID del equipo local.
            id_equipo_visita: UUID del equipo visitante.
            id_torneo:        UUID del torneo (para determinar reglas).
            marcador_local:   Tantos/sets del equipo local.
            marcador_visita:  Tantos/sets del equipo visitante.

        Returns:
            dict con los datos del resultado registrado.

        Raises:
            ResultadoInvalidoError: Si el marcador viola las reglas del deporte.
            RepositorioError:       Si falla la persistencia.
        """
        try:
            # 1. Obtener tipo de deporte del torneo
            torneo = self._torneo_repo.obtener_por_id(id_torneo)
            if not torneo:
                raise ValueError(f"Torneo {id_torneo} no encontrado.")
            tipo_deporte = torneo['tipo_deporte']

            # 2. Validar marcador según reglas del deporte
            torneo_obj = TorneoFactory.crear(
                tipo_deporte=tipo_deporte,
                nombre=torneo['nombre'],
                max_equipos=torneo['max_equipos'],
                fecha_inicio=torneo['fecha_inicio'],
            )
            if not torneo_obj.validar_resultado(marcador_local, marcador_visita):
                raise ResultadoInvalidoError(
                    f"El marcador {marcador_local}-{marcador_visita} no es válido "
                    f"para {tipo_deporte}."
                )

            # 3. Persistir resultado
            resultado = self._resultado_repo.guardar(
                id_partido, marcador_local, marcador_visita
            )

            # 4. Calcular puntos y actualizar estadísticas
            self._actualizar_estadisticas(
                id_torneo=id_torneo,
                id_local=id_equipo_local,
                id_visita=id_equipo_visita,
                marcador_local=marcador_local,
                marcador_visita=marcador_visita,
                tipo_deporte=tipo_deporte,
                torneo_obj=torneo_obj,
            )

            return resultado

        except ResultadoInvalidoError:
            raise
        except Exception as exc:
            logger.error(
                'ResultadoService.registrar_resultado -> id=%s │ error=%s',
                id_partido, exc,
            )
            raise RepositorioError(
                "Ocurrió un error técnico al registrar el resultado. Intente de nuevo."
            ) from exc

    def _actualizar_estadisticas(
        self,
        id_torneo: UUID,
        id_local: UUID,
        id_visita: UUID,
        marcador_local: int,
        marcador_visita: int,
        tipo_deporte: str,
        torneo_obj,
    ) -> None:
        """Calcula puntos y actualiza estadísticas de ambos equipos en la tabla."""
        reglas = _PUNTOS[tipo_deporte]

        pts_local = torneo_obj.calcular_puntos(marcador_local, marcador_visita)
        pts_visita = torneo_obj.calcular_puntos(marcador_visita, marcador_local)

        es_empate = marcador_local == marcador_visita

        stats_local = {
            'partidos_jugados': 1,
            'partidos_ganados': 1 if pts_local == reglas['victoria'] else 0,
            'partidos_empatados': 1 if es_empate else 0,
            'partidos_perdidos': 1 if pts_local == reglas['derrota'] and not es_empate else 0,
            'puntos': pts_local,
        }
        stats_visita = {
            'partidos_jugados': 1,
            'partidos_ganados': 1 if pts_visita == reglas['victoria'] else 0,
            'partidos_empatados': 1 if es_empate else 0,
            'partidos_perdidos': 1 if pts_visita == reglas['derrota'] and not es_empate else 0,
            'puntos': pts_visita,
        }

        # Actualizar tabla de posiciones
        for id_equipo, stats in [(id_local, stats_local), (id_visita, stats_visita)]:
            self._resultado_repo.actualizar_tabla(id_torneo, id_equipo, {
                'puntos': stats['puntos'],
                'pg': stats['partidos_ganados'],
                'pe': stats['partidos_empatados'],
                'pp': stats['partidos_perdidos'],
            })

    def ver_tabla(self, id_torneo: UUID) -> list:
        """Retorna la tabla de posiciones del torneo."""
        return self._resultado_repo.obtener_tabla(id_torneo)

    def ver_resultado(self, id_partido: UUID) -> dict | None:
        """Retorna el resultado de un partido específico."""
        return self._resultado_repo.obtener_por_partido(id_partido)
