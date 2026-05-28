"""
Repositorio de acceso a datos para 'fixtures' y 'partidos' — Neon.tech (psycopg2).
"""
import logging
from uuid import UUID

from app.exceptions import RepositorioError
from app.models.fixture import Fixture
from app.models.partido import Partido
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class PartidoRepository:
    """CRUD sobre 'fixtures' y 'partidos' usando psycopg2."""

    def guardar_fixture(self, fixture: Fixture) -> dict:
        """Persiste el fixture del torneo y retorna el registro creado."""
        sql = """
            INSERT INTO fixtures (id_torneo, total_jornadas)
            VALUES (%s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(fixture.id_torneo), fixture.total_jornadas))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("PartidoRepository.guardar_fixture -> %s", exc)
            raise RepositorioError("Error al guardar el fixture.") from exc
        finally:
            conn.close()

    def guardar_partidos(self, id_fixture: UUID, partidos: list) -> list:
        """Inserta en lote todos los partidos de un fixture dentro de una transacción."""
        sql = """
            INSERT INTO partidos (id_fixture, id_equipo_local, id_equipo_visita, jornada)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    registros = [
                        (str(id_fixture), str(p.id_equipo_local),
                         str(p.id_equipo_visita), p.jornada)
                        for p in partidos
                    ]
                    # executemany no retorna RETURNING; usamos execute en loop
                    resultados = []
                    for reg in registros:
                        cur.execute(sql, reg)
                        resultados.append(dict(cur.fetchone()))
                    return resultados
        except Exception as exc:
            logger.error("PartidoRepository.guardar_partidos -> %s", exc)
            raise RepositorioError("Error al guardar los partidos del fixture.") from exc
        finally:
            conn.close()

    def listar_por_torneo(self, id_torneo: UUID) -> list:
        """Retorna todos los partidos de un torneo ordenados por jornada."""
        sql = """
            SELECT p.*
            FROM partidos p
            INNER JOIN fixtures f ON f.id = p.id_fixture
            WHERE f.id_torneo = %s
            ORDER BY p.jornada
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_torneo),))
                    return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.error("PartidoRepository.listar_por_torneo -> %s", exc)
            raise RepositorioError("Error al listar partidos del torneo.") from exc
        finally:
            conn.close()

    def marcar_jugado(self, id_partido: UUID) -> dict:
        """Marca un partido como jugado."""
        sql = """
            UPDATE partidos
            SET jugado = TRUE, actualizado_en = NOW()
            WHERE id = %s
            RETURNING *
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_partido),))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("PartidoRepository.marcar_jugado -> %s", exc)
            raise RepositorioError("Error al actualizar estado del partido.") from exc
        finally:
            conn.close()

    def existe_fixture(self, id_torneo: UUID) -> bool:
        """Verifica si ya existe un fixture para el torneo."""
        sql = "SELECT id FROM fixtures WHERE id_torneo = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (str(id_torneo),))
                    return cur.fetchone() is not None
        except Exception as exc:
            logger.error("PartidoRepository.existe_fixture -> %s", exc)
            raise RepositorioError("Error al verificar existencia del fixture.") from exc
        finally:
            conn.close()
