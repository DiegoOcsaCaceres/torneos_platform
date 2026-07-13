"""
Repositorio de acceso a datos para la tabla 'Cancha' — Neon.tech (psycopg2).
"""
import logging

from app.exceptions import RepositorioError
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class CanchaRepository:
    """CRUD de solo lectura sobre la tabla 'Cancha' usando psycopg2."""

    def listar(self) -> list:
        """Retorna todas las canchas disponibles."""
        sql = "SELECT * FROM Cancha ORDER BY id_cancha"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("CanchaRepository.listar -> %s", exc)
            raise RepositorioError("Error al listar canchas.") from exc
        finally:
            conn.close()