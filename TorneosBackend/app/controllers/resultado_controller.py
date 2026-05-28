"""
Controller de Resultados.
Adaptado al nuevo schema: puntaje por Partido_Equipo, IDs enteros.
"""
from typing import Optional

from app.exceptions import ResultadoInvalidoError, RepositorioError
from app.services.resultado_service import ResultadoService


class ResultadoController:
    """Coordina el registro de resultados y la consulta de tabla de posiciones."""

    def __init__(self, resultado_service: ResultadoService) -> None:
        self._service = resultado_service

    def registrar(
        self,
        id_partido_str: str,
        id_pe_local_str: str,
        id_pe_visita_str: str,
        id_torneo_str: str,
        puntaje_local_str: str,
        puntaje_visita_str: str,
    ) -> tuple[bool, str, Optional[dict]]:
        """
        Registra el resultado de un partido.

        Args:
            id_partido_str:    ID del partido.
            id_pe_local_str:   ID del Partido_Equipo local.
            id_pe_visita_str:  ID del Partido_Equipo visitante.
            id_torneo_str:     ID del torneo.
            puntaje_local_str: Puntaje del equipo local (string desde consola).
            puntaje_visita_str:Puntaje del equipo visitante.

        Returns:
            Tupla (éxito, mensaje, datos_resultado).
        """
        try:
            id_partido = int(id_partido_str)
            id_pe_local = int(id_pe_local_str)
            id_pe_visita = int(id_pe_visita_str)
            id_torneo = int(id_torneo_str)
            puntaje_local = int(puntaje_local_str)
            puntaje_visita = int(puntaje_visita_str)

            resultado = self._service.registrar_resultado(
                id_partido=id_partido,
                id_partido_equipo_local=id_pe_local,
                id_partido_equipo_visita=id_pe_visita,
                id_torneo=id_torneo,
                puntaje_local=puntaje_local,
                puntaje_visita=puntaje_visita,
            )
            return (
                True,
                f"Resultado {puntaje_local}-{puntaje_visita} registrado correctamente.",
                resultado,
            )
        except ResultadoInvalidoError as exc:
            return False, str(exc), None
        except (ValueError, TypeError) as exc:
            return False, f"Datos inválidos: {exc}", None
        except RepositorioError as exc:
            return False, f"Error de base de datos: {exc}", None

    def ver_marcador(self, id_partido_str: str) -> tuple[bool, str, list]:
        """Retorna los puntajes de ambos equipos en un partido."""
        try:
            marcador = self._service.ver_marcador(int(id_partido_str))
            if not marcador:
                return True, "El partido aún no tiene resultado registrado.", []
            return True, "Marcador obtenido.", marcador
        except ValueError:
            return False, "ID de partido inválido.", []
        except RepositorioError as exc:
            return False, f"Error al consultar el marcador: {exc}", []

    def ver_tabla(self, id_torneo_str: str) -> tuple[bool, str, list]:
        """Retorna la tabla de posiciones del torneo."""
        try:
            tabla = self._service.ver_tabla(int(id_torneo_str))
            if not tabla:
                return True, "La tabla de posiciones está vacía.", []
            return True, "Tabla de posiciones obtenida.", tabla
        except ValueError:
            return False, "ID de torneo inválido.", []
        except RepositorioError as exc:
            return False, f"Error al obtener la tabla: {exc}", []
