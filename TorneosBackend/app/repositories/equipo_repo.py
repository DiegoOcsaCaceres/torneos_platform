"""
Repositorio de acceso a datos para la tabla 'equipos' — Neon.tech (psycopg2).
"""
import logging
from uuid import UUID

from app.exceptions import RepositorioError
from app.models.equipo import Equipo
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class EquipoRepository:
    """CRUD sobre la tabla 'equipos' usando psycopg2."""

    def guardar(self, equipo: Equipo) -> dict:
        """Inserta un nuevo equipo y retorna el registro creado."""
        sql = """
            INSERT INTO equipos (nombre, deporte, id_torneo)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (equipo.nombre, equipo.deporte, str(equipo.id_torneo)))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("EquipoRepository.guardar -> %s", exc)
            raise RepositorioError("Error interno al registrar el equipo.") from exc
        finally:
            conn.close()

    def existe_en_torneo(self, nombre: str, id_torneo: UUID) -> bool:
        """Verifica si ya existe un equipo con ese nombre en el torneo (RF-04)."""
        sql = "SELECT id FROM equipos WHERE nombre = %s AND id_torneo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (nombre, str(id_torneo)))
                    return cur.fetchone() is not None
        except Exception as exc:
            logger.error("EquipoRepository.existe_en_torneo -> %s", exc)
            raise RepositorioError("Error al verificar duplicidad de equipo.") from exc
        finally:
            conn.close()

    def listar_por_torneo(self, id_torneo: UUID) -> list:
        """Retorna todos los equipos activos de un torneo, ordenados por puntos."""
        sql = """
            SELECT * FROM equipos
            WHERE id_torneo = %s AND activo = TRUE
            ORDER BY puntos DESC
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_torneo),))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("EquipoRepository.listar_por_torneo -> %s", exc)
            raise RepositorioError("Error al listar equipos del torneo.") from exc
        finally:
            conn.close()

    def contar_en_torneo(self, id_torneo: UUID) -> int:
        """Cuenta los equipos activos en un torneo."""
        sql = "SELECT COUNT(*) AS total FROM equipos WHERE id_torneo = %s AND activo = TRUE"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_torneo),))
                    row = cur.fetchone()
                    return int(row['total']) if row else 0
        except Exception as exc:
            logger.error("EquipoRepository.contar_en_torneo -> %s", exc)
            raise RepositorioError("Error al contar equipos del torneo.") from exc
        finally:
            conn.close()

    def actualizar_estadisticas(self, id_equipo: UUID, datos: dict) -> dict:
        """
        Actualiza estadísticas de un equipo usando incrementos (+=).
        datos puede contener: puntos, partidos_jugados, partidos_ganados,
        partidos_empatados, partidos_perdidos.
        """
        campos = ", ".join(f"{k} = {k} + %s" for k in datos)
        sql = f"UPDATE equipos SET {campos}, actualizado_en = NOW() WHERE id = %s RETURNING *"
        valores = list(datos.values()) + [str(id_equipo)]
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, valores)
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("EquipoRepository.actualizar_estadisticas -> %s", exc)
            raise RepositorioError("Error al actualizar estadísticas del equipo.") from exc
        finally:
            conn.close()
