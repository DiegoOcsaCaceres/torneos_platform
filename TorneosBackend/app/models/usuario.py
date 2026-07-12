"""
Modelo de dominio: Usuario.
Representa a un usuario autenticable de la plataforma.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    """
    Entidad que representa un usuario del sistema.

    Attributes:
        nombres:            Nombre(s) del usuario.
        apellido_paterno:   Apellido paterno.
        apellido_materno:   Apellido materno.
        email:              Correo electrónico, único en el sistema.
        password_hash:      Hash bcrypt de la contraseña (nunca texto plano).
        rol:                Rol del usuario. Por defecto 'ORGANIZADOR'.
        activo:             Indica si la cuenta está habilitada.
        id_usuario:         ID asignado tras la persistencia.
        fecha_registro:     Fecha de creación de la cuenta.
    """
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    password_hash: str
    rol: str = 'ORGANIZADOR'
    activo: bool = True
    id_usuario: Optional[int] = field(default=None)
    fecha_registro: Optional[datetime] = field(default=None)

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario."""
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    def __str__(self) -> str:
        return f"[Usuario #{self.id_usuario}] {self.nombre_completo} ({self.email})"