"""
Repositorio de acceso a datos para la tabla 'Jugador' — Neon.tech (psycopg2).
"""
import logging

from app.exceptions import RepositorioError
from app.models.jugador import Jugador
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class JugadorRepository:
    """CRUD sobre la tabla 'Jugador' usando psycopg2."""

    def guardar(self, jugador: Jugador) -> dict:
        """Inserta un nuevo jugador y retorna el registro creado."""
        sql = """
            INSERT INTO Jugador (nombre_jugador, apellido_paterno, apellido_materno, DNI, id_equipo)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        jugador.nombre_jugador,
                        jugador.apellido_paterno,
                        jugador.apellido_materno,
                        jugador.DNI,
                        jugador.id_equipo,
                    ))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("JugadorRepository.guardar -> %s", exc)
            raise RepositorioError("Error interno al registrar el jugador.") from exc
        finally:
            conn.close()

    def existe_dni(self, dni: str) -> bool:
        """Verifica si ya existe un jugador con ese DNI (único en todo el sistema)."""
        sql = "SELECT id_jugador FROM Jugador WHERE DNI = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (dni,))
                    return cur.fetchone() is not None
        except Exception as exc:
            logger.error("JugadorRepository.existe_dni -> %s", exc)
            raise RepositorioError("Error al verificar duplicidad de DNI.") from exc
        finally:
            conn.close()

    def listar_por_equipo(self, id_equipo: int) -> list:
        """Retorna todos los jugadores de un equipo."""
        sql = """
            SELECT * FROM Jugador
            WHERE id_equipo = %s
            ORDER BY id_jugador
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_equipo,))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("JugadorRepository.listar_por_equipo -> %s", exc)
            raise RepositorioError("Error al listar jugadores del equipo.") from exc
        finally:
            conn.close()

    def contar_por_equipo(self, id_equipo: int) -> int:
        """Cuenta los jugadores en un equipo."""
        sql = "SELECT COUNT(*) AS total FROM Jugador WHERE id_equipo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_equipo,))
                    row = cur.fetchone()
                    return int(row['total']) if row else 0
        except Exception as exc:
            logger.error("JugadorRepository.contar_por_equipo -> %s", exc)
            raise RepositorioError("Error al contar jugadores del equipo.") from exc
        finally:
            conn.close()