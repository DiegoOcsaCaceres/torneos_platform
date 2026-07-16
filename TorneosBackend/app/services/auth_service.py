"""
Servicio de autenticación: registro, login y validación de tokens JWT.
"""
import re
import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError

from app.exceptions import (
    UsuarioDuplicadoError,
    CredencialesInvalidasError,
    RepositorioError,
)
from app.models.usuario import Usuario
from app.repositories.usuario_repo import UsuarioRepository
from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HORAS

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class AuthService:
    """Orquesta el registro, login y verificación de sesión de usuarios."""

    def __init__(self, usuario_repo: UsuarioRepository) -> None:
        self._usuario_repo = usuario_repo

    # ── Registro ─────────────────────────────────────────────────────────

    def registrar(
        self,
        nombres: str,
        apellido_paterno: str,
        apellido_materno: str,
        email: str,
        password: str,
    ) -> dict:
        """
        Valida los datos, hashea la contraseña y crea el usuario.

        Raises:
            ValueError:             Si algún dato es inválido.
            UsuarioDuplicadoError:  Si el email ya está registrado.
            RepositorioError:       Si falla la persistencia.
        """
        nombres = (nombres or '').strip()
        apellido_paterno = (apellido_paterno or '').strip()
        apellido_materno = (apellido_materno or '').strip()
        email = (email or '').strip().lower()

        if not nombres or not apellido_paterno or not apellido_materno:
            raise ValueError("Nombres y apellidos son obligatorios.")

        if not EMAIL_REGEX.match(email):
            raise ValueError("El formato del correo electrónico no es válido.")

        if not password or len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")

        if self._usuario_repo.existe_email(email):
            raise UsuarioDuplicadoError(
                f"Ya existe una cuenta registrada con el correo '{email}'."
            )

        password_hash = self._hashear_password(password)

        usuario = Usuario(
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            email=email,
            password_hash=password_hash,
        )
        return self._usuario_repo.guardar(usuario)

    # ── Actualización de datos personales ────────────────────────────────

    def actualizar_perfil(
        self,
        id_usuario: int,
        nombres: str,
        apellido_paterno: str,
        apellido_materno: str,
    ) -> dict:
        """
        Valida y actualiza nombres/apellidos de un usuario existente.

        Raises:
            ValueError:       Si algún dato es inválido o está en blanco.
            RepositorioError: Si falla la persistencia.
        """
        nombres = (nombres or '').strip()
        apellido_paterno = (apellido_paterno or '').strip()
        apellido_materno = (apellido_materno or '').strip()

        if not nombres or not apellido_paterno or not apellido_materno:
            raise ValueError("Nombres y apellidos son obligatorios.")

        return self._usuario_repo.actualizar_datos(
            id_usuario, nombres, apellido_paterno, apellido_materno
        )

    # ── Cambio de contraseña ─────────────────────────────────────────────

    def cambiar_password(self, email: str, password_actual: str, password_nueva: str) -> None:
        """
        Verifica la contraseña actual y, si es correcta, la reemplaza por la nueva.

        Raises:
            CredencialesInvalidasError: Si la contraseña actual no coincide.
            ValueError:                 Si la nueva contraseña es inválida.
            RepositorioError:           Si falla la persistencia.
        """
        usuario_row = self._usuario_repo.obtener_por_email(email)
        if not usuario_row:
            raise CredencialesInvalidasError("Usuario no encontrado.")

        if not self._verificar_password(password_actual, usuario_row['password_hash']):
            raise CredencialesInvalidasError("La contraseña actual no es correcta.")

        if not password_nueva or len(password_nueva) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres.")

        nuevo_hash = self._hashear_password(password_nueva)
        self._usuario_repo.actualizar_password(usuario_row['id_usuario'], nuevo_hash)

    # ── Login ────────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> dict:
        """
        Verifica credenciales y retorna un token JWT junto con los datos del usuario.

        Raises:
            CredencialesInvalidasError: Si el email no existe o la contraseña no coincide.
            RepositorioError:           Si falla la consulta a la BD.
        """
        email = (email or '').strip().lower()
        usuario_row = self._usuario_repo.obtener_por_email(email)

        if not usuario_row:
            raise CredencialesInvalidasError("El correo o la contraseña son incorrectos.")

        if not usuario_row.get('activo', True):
            raise CredencialesInvalidasError("Esta cuenta se encuentra deshabilitada.")

        if not self._verificar_password(password, usuario_row['password_hash']):
            raise CredencialesInvalidasError("El correo o la contraseña son incorrectos.")

        token = self._generar_token(usuario_row)

        usuario_row.pop('password_hash', None)
        return {'token': token, 'usuario': usuario_row}

    # ── Verificación de sesión ──────────────────────────────────────────

    def verificar_token(self, token: str) -> dict:
        """
        Decodifica y valida un token JWT.

        Raises:
            CredencialesInvalidasError: Si el token es inválido o expiró.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError as exc:
            raise CredencialesInvalidasError("Sesión inválida o expirada.") from exc

    # ── Métodos privados ─────────────────────────────────────────────────

    @staticmethod
    def _hashear_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def _verificar_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def _generar_token(usuario_row: dict) -> str:
        expiracion = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HORAS)
        payload = {
            'sub': str(usuario_row['id_usuario']),
            'email': usuario_row['email'],
            'rol': usuario_row.get('rol', 'ORGANIZADOR'),
            'exp': expiracion,
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)