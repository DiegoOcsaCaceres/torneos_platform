"""
Repositorio de acceso a datos para la tabla 'Jugador' — Neon.tech (psycopg2).
"""
import logging
from typing import Optional

from app.exceptions import RepositorioError
from app.models.jugador import Jugador
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class JugadorRepository:
    """CRUD sobre la tabla 'Jugador' usando psycopg2."""

    def guardar(self, jugador: Jugador) -> dict:
        """Inserta un nuevo jugador y retorna el registro creado."""
        sql = """
            INSERT INTO Jugador (nombre_jugador, apellido_paterno, apellido_materno, DNI, id_equipo, edad, foto)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                        jugador.edad,
                        jugador.foto,
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

    def obtener_por_id(self, id_jugador: int) -> Optional[dict]:
        """Busca un jugador por su ID. Retorna None si no existe."""
        sql = "SELECT * FROM Jugador WHERE id_jugador = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_jugador,))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("JugadorRepository.obtener_por_id -> %s", exc)
            raise RepositorioError("Error al consultar el jugador.") from exc
        finally:
            conn.close()

    def actualizar(
        self,
        id_jugador: int,
        nombre_jugador: str,
        apellido_paterno: str,
        apellido_materno: str,
        dni: str,
        edad: Optional[int] = None,
        foto: Optional[str] = None,
    ) -> dict:
        """Actualiza los datos de un jugador."""
        sql = """
            UPDATE Jugador
            SET nombre_jugador = %s, apellido_paterno = %s, apellido_materno = %s, DNI = %s,
                edad = %s, foto = %s
            WHERE id_jugador = %s
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        nombre_jugador, apellido_paterno, apellido_materno, dni,
                        edad, foto, id_jugador,
                    ))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("JugadorRepository.actualizar -> %s", exc)
            raise RepositorioError("Error al actualizar el jugador.") from exc
        finally:
            conn.close()

    def eliminar(self, id_jugador: int) -> None:
        """Elimina un jugador por su ID."""
        sql = "DELETE FROM Jugador WHERE id_jugador = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_jugador,))
        except Exception as exc:
            logger.error("JugadorRepository.eliminar -> %s", exc)
            raise RepositorioError("Error al eliminar el jugador.") from exc
        finally:
            conn.close()

    