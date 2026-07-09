"""
Repositorio de acceso a datos para la tabla 'Usuario' — Neon.tech (psycopg2).
"""
import logging
from typing import Optional

from app.exceptions import RepositorioError
from app.models.usuario import Usuario
from config.database import obtener_conexion

logger = logging.getLogger(__name__)


class UsuarioRepository:
    """CRUD sobre la tabla 'Usuario' usando psycopg2."""

    def guardar(self, usuario: Usuario) -> dict:
        """Inserta un nuevo usuario y retorna el registro creado."""
        sql = """
            INSERT INTO Usuario (nombres, apellido_paterno, apellido_materno,
                                  email, password_hash, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_usuario, nombres, apellido_paterno, apellido_materno,
                      email, rol, activo, fecha_registro
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        usuario.nombres,
                        usuario.apellido_paterno,
                        usuario.apellido_materno,
                        usuario.email,
                        usuario.password_hash,
                        usuario.rol,
                        usuario.activo,
                    ))
                    return dict(cur.fetchone())
        except Exception as exc:
            logger.error("UsuarioRepository.guardar -> %s", exc)
            raise RepositorioError("Error interno al registrar el usuario.") from exc
        finally:
            conn.close()

    def obtener_por_email(self, email: str) -> Optional[dict]:
        """
        Busca un usuario por su email. Retorna None si no existe.
        Incluye password_hash (uso interno para validar login).
        """
        sql = "SELECT * FROM Usuario WHERE email = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (email,))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("UsuarioRepository.obtener_por_email -> %s", exc)
            raise RepositorioError("Error al consultar el usuario.") from exc
        finally:
            conn.close()

    def existe_email(self, email: str) -> bool:
        """Verifica si ya existe un usuario registrado con ese email."""
        sql = "SELECT id_usuario FROM Usuario WHERE email = %s"
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (email,))
                    return cur.fetchone() is not None
        except Exception as exc:
            logger.error("UsuarioRepository.existe_email -> %s", exc)
            raise RepositorioError("Error al verificar el correo.") from exc
        finally:
            conn.close()

    def obtener_por_id(self, id_usuario: int) -> Optional[dict]:
        """Busca un usuario por su ID (sin exponer password_hash)."""
        sql = """
            SELECT id_usuario, nombres, apellido_paterno, apellido_materno,
                   email, rol, activo, fecha_registro
            FROM Usuario
            WHERE id_usuario = %s
        """
        conn = obtener_conexion()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (id_usuario,))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as exc:
            logger.error("UsuarioRepository.obtener_por_id -> %s", exc)
            raise RepositorioError("Error al consultar el usuario.") from exc
        finally:
            conn.close()