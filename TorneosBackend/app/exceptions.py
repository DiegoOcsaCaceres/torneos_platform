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
