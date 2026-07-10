"""
Excepciones personalizadas del dominio de torneos.
"""


class RepositorioError(Exception):
    """Error genérico de acceso a datos."""


class TorneoNoEncontradoError(Exception):
    """El torneo solicitado no existe en la BD."""


class EquipoDuplicadoError(Exception):
    """Ya existe un equipo con ese nombre en el torneo."""


class FixtureError(Exception):
    """Error al generar o consultar el fixture."""


class ResultadoInvalidoError(Exception):
    """El marcador proporcionado viola las reglas del deporte."""

class UsuarioDuplicadoError(Exception):
    """Ya existe un usuario registrado con ese correo electrónico."""


class CredencialesInvalidasError(Exception):
    """El correo o la contraseña no son correctos."""

class CredencialesInvalidasError(Exception):
    """El correo o la contraseña no son correctos."""

class JugadorDuplicadoError(Exception):
    """Ya existe un jugador registrado con ese DNI."""