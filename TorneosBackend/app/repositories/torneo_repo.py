"""
Repositorio de acceso a datos para las tablas 'Torneo' y 'Deporte' — Neon.tech (psycopg2).
"""
import logging
from typing import Optional

from app.exceptions import RepositorioError, TorneoNoEncontradoError
from app.models.torneo import Torneo
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class TorneoRepository:
    """CRUD sobre las tablas 'Torneo' y 'Deporte' usando psycopg2."""

    def guardar(self, torneo: Torneo) -> dict:
        """Inserta un nuevo torneo y retorna el registro creado."""
        sql = """
            INSERT INTO Torneo (nombre_torneo, fecha_inicio, numero_equipos, id_deporte, formato, jugadores_por_equipo, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        torneo.nombre_torneo,
                        torneo.fecha_inicio,
                        torneo.numero_equipos,
                        torneo.id_deporte,
                        torneo.formato,
                        torneo.jugadores_por_equipo,
                        torneo.id_usuario,
                    ))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("TorneoRepository.guardar -> %s", exc)
            raise RepositorioError("Error interno al crear el torneo.") from exc
        finally:
            conn.close()

    def obtener_por_id(self, id_torneo: int, id_usuario: Optional[int] = None) -> Optional[dict]:
        """
        Busca un torneo por su ID. Retorna None si no existe.

        Si se pasa id_usuario, solo retorna el torneo si pertenece a esa cuenta;
        de lo contrario retorna None (evita filtrar torneos de otras cuentas).
        """
        sql = """
            SELECT t.*, d.nombre_deporte, d.reglas
            FROM Torneo t
            JOIN Deporte d ON d.id_deporte = t.id_deporte
            WHERE t.id_torneo = %s
        """
        parametros = [id_torneo]
        if id_usuario is not None:
            sql += " AND t.id_usuario = %s"
            parametros.append(id_usuario)

        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, tuple(parametros))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("TorneoRepository.obtener_por_id -> %s", exc)
            raise RepositorioError("Error al consultar el torneo.") from exc
        finally:
            conn.close()

    def listar(self, id_usuario: Optional[int] = None) -> list:
        """
        Retorna los torneos con el nombre de su deporte.

        Si se pasa id_usuario, solo retorna los torneos de esa cuenta, para que
        cada cuenta vea únicamente los torneos que ella misma creó.
        """
        sql = """
            SELECT t.*, d.nombre_deporte
            FROM Torneo t
            JOIN Deporte d ON d.id_deporte = t.id_deporte
        """
        parametros = ()
        if id_usuario is not None:
            sql += " WHERE t.id_usuario = %s"
            parametros = (id_usuario,)
        sql += " ORDER BY t.id_torneo"

        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, parametros)
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("TorneoRepository.listar -> %s", exc)
            raise RepositorioError("Error al listar los torneos.") from exc
        finally:
            conn.close()

    def listar_deportes(self) -> list:
        """Retorna todos los deportes disponibles."""
        sql = "SELECT * FROM Deporte ORDER BY id_deporte"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("TorneoRepository.listar_deportes -> %s", exc)
            raise RepositorioError("Error al listar deportes.") from exc
        finally:
            conn.close()

    def eliminar(self, id_torneo: int) -> None:
        """Elimina un torneo por su ID."""
        sql = "DELETE FROM Torneo WHERE id_torneo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_torneo,))
        except Exception as exc:
            logger.error("TorneoRepository.eliminar -> %s", exc)
            raise RepositorioError("Error al eliminar el torneo.") from exc
        finally:
            conn.close()
