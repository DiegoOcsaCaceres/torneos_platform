"""
Punto de entrada de la aplicación de gestión de torneos.
Adaptado al nuevo schema con tablas: Deporte, Torneo, Equipo, Jugador,
Cancha, Condicion, Partido, Partido_Equipo, Resultado.
"""
from app.repositories.torneo_repo import TorneoRepository
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.partido_repo import PartidoRepository
from app.repositories.resultado_repo import ResultadoRepository

from app.services.torneo_service import TorneoService
from app.services.inscripcion_service import InscripcionService
from app.services.fixture_service import FixtureService
from app.services.resultado_service import ResultadoService

from app.controllers.torneo_controller import TorneoController
from app.controllers.inscripcion_controller import InscripcionController
from app.controllers.fixture_controller import FixtureController
from app.controllers.resultado_controller import ResultadoController

from app.views.menu_principal import MenuPrincipal


def main():
    # ── Repositorios ─────────────────────────────────────────────────────
    torneo_repo    = TorneoRepository()
    equipo_repo    = EquipoRepository()
    partido_repo   = PartidoRepository()
    resultado_repo = ResultadoRepository()

    # ── Servicios ─────────────────────────────────────────────────────────
    torneo_service     = TorneoService(torneo_repo)
    inscripcion_service = InscripcionService(equipo_repo, torneo_repo)
    fixture_service    = FixtureService(partido_repo, equipo_repo)
    resultado_service  = ResultadoService(resultado_repo, partido_repo, torneo_repo)

    # ── Controllers ───────────────────────────────────────────────────────
    torneo_ctrl     = TorneoController(torneo_service)
    inscripcion_ctrl = InscripcionController(inscripcion_service)
    fixture_ctrl    = FixtureController(fixture_service)
    resultado_ctrl  = ResultadoController(resultado_service)

    # ── Vista principal ───────────────────────────────────────────────────
    menu = MenuPrincipal(
        torneo_ctrl=torneo_ctrl,
        inscripcion_ctrl=inscripcion_ctrl,
        fixture_ctrl=fixture_ctrl,
        resultado_ctrl=resultado_ctrl,
    )
    menu.ejecutar()


if __name__ == '__main__':
    main()
