"""
Repositorio de acceso a datos para la tabla 'torneos' — Neon.tech (psycopg2).
"""
import logging
from typing import Optional
from uuid import UUID

from app.exceptions import RepositorioError, TorneoNoEncontradoError
from app.models.torneo import Torneo
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class TorneoRepository:
    """CRUD sobre la tabla 'torneos' usando psycopg2."""

    # ── helpers internos ──────────────────────────────────────────────────
    @staticmethod
    def _ejecutar(sql: str, params: tuple = (), fetchone=False, fetchall=False):
        """Ejecuta una sentencia SQL y retorna el resultado esperado."""
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    if fetchone:
                        return dict(cur.fetchone()) if cur.rowcount != 0 else None
                    if fetchall:
                        rows = cur.fetchall()
                        return [dict(r) for r in rows]
                    # Para INSERT ... RETURNING fetchone también aplica
                    if cur.description:
                        row = cur.fetchone()
                        return dict(row) if row else None
        except Exception as exc:
            raise exc
        finally:
            conn.close()

    # ── operaciones públicas ──────────────────────────────────────────────
    def guardar(self, torneo: Torneo) -> dict:
        """Inserta un nuevo torneo y retorna el registro creado."""
        sql = """
            INSERT INTO torneos (nombre, tipo_deporte, max_equipos, fecha_inicio, estado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        try:
            resultado = self._ejecutar(
                sql,
                (torneo.nombre, torneo.tipo_deporte, torneo.max_equipos,
                 torneo.fecha_inicio, torneo.estado),
            )
            return resultado
        except Exception as exc:
            logger.error("TorneoRepository.guardar -> %s", exc)
            raise RepositorioError("Error interno al crear el torneo.") from exc

    def obtener_por_id(self, id_torneo: UUID) -> Optional[dict]:
        """Busca un torneo por su UUID. Retorna None si no existe."""
        sql = "SELECT * FROM torneos WHERE id = %s"
        try:
            conn = obtener_conexion()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(sql, (str(id_torneo),))
                        row = cur.fetchone()
                        return dict(row) if row else None
            finally:
                conn.close()
        except Exception as exc:
            logger.error("TorneoRepository.obtener_por_id -> %s", exc)
            raise RepositorioError("Error al consultar el torneo.") from exc

    def listar(self) -> list:
        """Retorna todos los torneos ordenados por fecha de creación."""
        sql = "SELECT * FROM torneos ORDER BY creado_en DESC"
        try:
            return self._ejecutar(sql, fetchall=True) or []
        except Exception as exc:
            logger.error("TorneoRepository.listar -> %s", exc)
            raise RepositorioError("Error al listar los torneos.") from exc

    def actualizar_estado(self, id_torneo: UUID, nuevo_estado: str) -> dict:
        """Actualiza el estado de un torneo existente."""
        sql = """
            UPDATE torneos
            SET estado = %s, actualizado_en = NOW()
            WHERE id = %s
            RETURNING *
        """
        try:
            resultado = self._ejecutar(sql, (nuevo_estado, str(id_torneo)))
            if not resultado:
                raise TorneoNoEncontradoError(f"Torneo {id_torneo} no encontrado.")
            return resultado
        except TorneoNoEncontradoError:
            raise
        except Exception as exc:
            logger.error("TorneoRepository.actualizar_estado -> %s", exc)
            raise RepositorioError("Error al actualizar el estado del torneo.") from exc
