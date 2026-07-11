"""
Repositorio de acceso a datos para la tabla 'Resultado' — Neon.tech (psycopg2).
"""
import logging
from typing import Optional

from app.exceptions import RepositorioError
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class ResultadoRepository:
    """CRUD sobre la tabla 'Resultado' usando psycopg2."""

    def guardar(self, puntaje: int, id_partido_equipo: int, penales: Optional[int] = None) -> dict:
        """
        Persiste el puntaje de un equipo en un partido.

        El parámetro `penales` solo se usa en Torneo Relámpago, cuando el
        partido se definió por tanda de penales. En Liga siempre queda None.
        """
        sql = """
            INSERT INTO Resultado (puntaje, id_partido_equipo, penales_local, penales_visita)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    # El mismo valor de penales se guarda tanto en penales_local como
                    # en penales_visita para esta fila; se resuelve cuál corresponde
                    # a cada lado al leer el marcador (ver obtener_marcador_partido).
                    cur.execute(sql, (puntaje, id_partido_equipo, penales, penales))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("ResultadoRepository.guardar -> %s", exc)
            raise RepositorioError("Error al guardar el resultado.") from exc
        finally:
            conn.close()

    def obtener_por_partido_equipo(self, id_partido_equipo: int) -> Optional[dict]:
        """Retorna el resultado de un Partido_Equipo específico."""
        sql = "SELECT * FROM Resultado WHERE id_partido_equipo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_partido_equipo,))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("ResultadoRepository.obtener_por_partido_equipo -> %s", exc)
            raise RepositorioError("Error al consultar el resultado.") from exc
        finally:
            conn.close()

    def obtener_marcador_partido(self, id_partido: int) -> list:
        """
        Retorna los puntajes de ambos equipos de un partido.
        Incluye nombre del equipo y su condición (Local/Visitante).
        """
        sql = """
            SELECT
                r.id_resultado,
                r.puntaje,
                e.nombre_equipo,
                c.nombre_condicion,
                pe.id_partido_equipo
            FROM Resultado r
            JOIN Partido_Equipo pe ON pe.id_partido_equipo = r.id_partido_equipo
            JOIN Equipo    e  ON e.id_equipo   = pe.id_equipo
            JOIN Condicion c  ON c.id_condicion = pe.id_condicion
            WHERE pe.id_partido = %s
            ORDER BY pe.id_condicion
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_partido,))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("ResultadoRepository.obtener_marcador_partido -> %s", exc)
            raise RepositorioError("Error al obtener el marcador del partido.") from exc
        finally:
            conn.close()

    def obtener_tabla_posiciones(self, id_torneo: int) -> list:
        """
        Calcula la tabla de posiciones de un torneo sumando puntajes por equipo.
        Retorna los equipos ordenados por puntaje total descendente.
        """
        sql = """
            SELECT
                e.id_equipo,
                e.nombre_equipo,
                COALESCE(SUM(r.puntaje), 0)           AS puntos_totales,
                COUNT(pe.id_partido_equipo)            AS partidos_jugados,
                COUNT(CASE WHEN r.puntaje = (
                    SELECT MAX(r2.puntaje)
                    FROM Resultado r2
                    JOIN Partido_Equipo pe2 ON pe2.id_partido_equipo = r2.id_partido_equipo
                    WHERE pe2.id_partido = pe.id_partido
                ) THEN 1 END)                          AS partidos_ganados
            FROM Equipo e
            JOIN Partido_Equipo pe ON pe.id_equipo = e.id_equipo
            JOIN Partido p         ON p.id_partido = pe.id_partido
                                  AND p.id_torneo  = %s
                                  AND p.estado     = 'Finalizado'
            LEFT JOIN Resultado r  ON r.id_partido_equipo = pe.id_partido_equipo
            GROUP BY e.id_equipo, e.nombre_equipo
            ORDER BY puntos_totales DESC
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_torneo,))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("ResultadoRepository.obtener_tabla_posiciones -> %s", exc)
            raise RepositorioError("Error al obtener la tabla de posiciones.") from exc
        finally:
            conn.close()
