"""
Repositorio de acceso a datos para 'resultados' y 'tabla_posiciones' — Neon.tech (psycopg2).
"""
import logging
from uuid import UUID

from app.exceptions import RepositorioError
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class ResultadoRepository:
    """CRUD sobre 'resultados' y 'tabla_posiciones' usando psycopg2."""

    def guardar(self, id_partido: UUID, marcador_local: int, marcador_visita: int) -> dict:
        """Persiste el resultado de un partido."""
        sql = """
            INSERT INTO resultados (id_partido, marcador_local, marcador_visita)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_partido), marcador_local, marcador_visita))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("ResultadoRepository.guardar -> %s", exc)
            raise RepositorioError("Error al guardar el resultado.") from exc
        finally:
            conn.close()

    def obtener_por_partido(self, id_partido: UUID) -> dict | None:
        """Retorna el resultado de un partido, o None si no existe."""
        sql = "SELECT * FROM resultados WHERE id_partido = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_partido),))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("ResultadoRepository.obtener_por_partido -> %s", exc)
            raise RepositorioError("Error al consultar el resultado.") from exc
        finally:
            conn.close()

    def obtener_tabla(self, id_torneo: UUID) -> list:
        """Retorna la tabla de posiciones con el nombre del equipo, ordenada por puntos."""
        sql = """
            SELECT tp.*, e.nombre AS nombre_equipo
            FROM tabla_posiciones tp
            INNER JOIN equipos e ON e.id = tp.id_equipo
            WHERE tp.id_torneo = %s
            ORDER BY tp.puntos DESC, tp.pg DESC
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_torneo),))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("ResultadoRepository.obtener_tabla -> %s", exc)
            raise RepositorioError("Error al obtener la tabla de posiciones.") from exc
        finally:
            conn.close()

    def actualizar_tabla(self, id_torneo: UUID, id_equipo: UUID, datos: dict) -> dict:
        """
        Upsert en tabla_posiciones: crea la fila si no existe,
        o incrementa los contadores si ya existe.
        """
        sql = """
            INSERT INTO tabla_posiciones (id_torneo, id_equipo, puntos, pg, pe, pp)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_torneo, id_equipo)
            DO UPDATE SET
                puntos = tabla_posiciones.puntos + EXCLUDED.puntos,
                pg     = tabla_posiciones.pg + EXCLUDED.pg,
                pe     = tabla_posiciones.pe + EXCLUDED.pe,
                pp     = tabla_posiciones.pp + EXCLUDED.pp,
                actualizado_en = NOW()
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        str(id_torneo), str(id_equipo),
                        datos.get('puntos', 0),
                        datos.get('pg', 0),
                        datos.get('pe', 0),
                        datos.get('pp', 0),
                    ))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("ResultadoRepository.actualizar_tabla -> %s", exc)
            raise RepositorioError("Error al actualizar la tabla de posiciones.") from exc
        finally:
            conn.close()
