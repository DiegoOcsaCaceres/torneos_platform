"""
Repositorio de acceso a datos para la tabla 'Equipo' — Neon.tech (psycopg2).
"""
import logging

from app.exceptions import RepositorioError
from app.models.equipo import Equipo
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class EquipoRepository:
    """CRUD sobre la tabla 'Equipo' usando psycopg2."""

    def guardar(self, equipo: Equipo) -> dict:
        """Inserta un nuevo equipo y retorna el registro creado."""
        sql = """
            INSERT INTO Equipo (nombre_equipo, numero_jugadores, id_torneo)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        equipo.nombre_equipo,
                        equipo.numero_jugadores,
                        equipo.id_torneo,
                    ))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("EquipoRepository.guardar -> %s", exc)
            raise RepositorioError("Error interno al registrar el equipo.") from exc
        finally:
            conn.close()

    def existe_en_torneo(self, nombre_equipo: str, id_torneo: int) -> bool:
        """Verifica si ya existe un equipo con ese nombre en el torneo."""
        sql = "SELECT id_equipo FROM Equipo WHERE nombre_equipo = %s AND id_torneo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (nombre_equipo, id_torneo))
                    return cur.fetchone() is not None
        except Exception as exc:
            logger.error("EquipoRepository.existe_en_torneo -> %s", exc)
            raise RepositorioError("Error al verificar duplicidad de equipo.") from exc
        finally:
            conn.close()

    def listar_por_torneo(self, id_torneo: int) -> list:
        """Retorna todos los equipos de un torneo."""
        sql = """
            SELECT * FROM Equipo
            WHERE id_torneo = %s
            ORDER BY id_equipo
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_torneo,))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("EquipoRepository.listar_por_torneo -> %s", exc)
            raise RepositorioError("Error al listar equipos del torneo.") from exc
        finally:
            conn.close()

    def contar_en_torneo(self, id_torneo: int) -> int:
        """Cuenta los equipos en un torneo."""
        sql = "SELECT COUNT(*) AS total FROM Equipo WHERE id_torneo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_torneo,))
                    row = cur.fetchone()
                    return int(row['total']) if row else 0
        except Exception as exc:
            logger.error("EquipoRepository.contar_en_torneo -> %s", exc)
            raise RepositorioError("Error al contar equipos del torneo.") from exc
        finally:
            conn.close()
