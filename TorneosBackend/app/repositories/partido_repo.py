"""
Repositorio de acceso a datos para 'Partido' y 'Partido_Equipo' — Neon.tech (psycopg2).
"""
import logging
from typing import Optional

from app.exceptions import RepositorioError
from app.models.partido import Partido
from app.models.partido_equipo import PartidoEquipo
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class PartidoRepository:
    """CRUD sobre 'Partido' y 'Partido_Equipo' usando psycopg2."""

    def guardar_partido(self, partido: Partido) -> dict:
        """Persiste un partido y retorna el registro creado."""
        sql = """
            INSERT INTO Partido (fecha, hora, estado, id_cancha, id_torneo)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        partido.fecha,
                        partido.hora,
                        partido.estado,
                        partido.id_cancha,
                        partido.id_torneo,
                    ))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("PartidoRepository.guardar_partido -> %s", exc)
            raise RepositorioError("Error al guardar el partido.") from exc
        finally:
            conn.close()

    def guardar_partido_equipo(self, pe: PartidoEquipo) -> dict:
        """Inserta una relación Partido_Equipo y retorna el registro creado."""
        sql = """
            INSERT INTO Partido_Equipo (id_partido, id_equipo, id_condicion)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (pe.id_partido, pe.id_equipo, pe.id_condicion))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("PartidoRepository.guardar_partido_equipo -> %s", exc)
            raise RepositorioError("Error al guardar Partido_Equipo.") from exc
        finally:
            conn.close()

    def listar_por_torneo(self, id_torneo: int) -> list:
        """
        Retorna todos los partidos de un torneo con sus equipos y condiciones.
        Cada fila incluye datos del partido más local y visitante.
        """
        sql = """
            SELECT
                p.id_partido,
                p.fecha,
                p.hora,
                p.estado,
                p.id_cancha,
                p.id_torneo,
                e_local.nombre_equipo  AS equipo_local,
                e_visit.nombre_equipo  AS equipo_visitante,
                pe_local.id_partido_equipo  AS id_pe_local,
                pe_visit.id_partido_equipo  AS id_pe_visitante
            FROM Partido p
            JOIN Partido_Equipo pe_local  ON pe_local.id_partido  = p.id_partido
                                         AND pe_local.id_condicion = 1
            JOIN Partido_Equipo pe_visit  ON pe_visit.id_partido  = p.id_partido
                                         AND pe_visit.id_condicion = 2
            JOIN Equipo e_local   ON e_local.id_equipo  = pe_local.id_equipo
            JOIN Equipo e_visit   ON e_visit.id_equipo  = pe_visit.id_equipo
            WHERE p.id_torneo = %s
            ORDER BY p.fecha, p.hora
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_torneo,))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("PartidoRepository.listar_por_torneo -> %s", exc)
            raise RepositorioError("Error al listar partidos del torneo.") from exc
        finally:
            conn.close()

    def obtener_partido_equipo(self, id_partido_equipo: int) -> Optional[dict]:
        """Retorna un registro de Partido_Equipo por su ID."""
        sql = "SELECT * FROM Partido_Equipo WHERE id_partido_equipo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_partido_equipo,))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("PartidoRepository.obtener_partido_equipo -> %s", exc)
            raise RepositorioError("Error al consultar Partido_Equipo.") from exc
        finally:
            conn.close()

    def listar_canchas(self) -> list:
        """Retorna todas las canchas disponibles."""
        sql = "SELECT * FROM Cancha ORDER BY id_cancha"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("PartidoRepository.listar_canchas -> %s", exc)
            raise RepositorioError("Error al listar canchas.") from exc
        finally:
            conn.close()

    def actualizar_estado(self, id_partido: int, nuevo_estado: str) -> dict:
        """Actualiza el estado de un partido."""
        sql = "UPDATE Partido SET estado = %s WHERE id_partido = %s RETURNING *"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (nuevo_estado, id_partido))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("PartidoRepository.actualizar_estado -> %s", exc)
            raise RepositorioError("Error al actualizar estado del partido.") from exc
        finally:
            conn.close()
