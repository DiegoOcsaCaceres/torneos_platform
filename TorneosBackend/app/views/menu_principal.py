"""
Vista: Menú Principal.
Solo responsabilidad: mostrar opciones y leer entradas del usuario.
Ninguna lógica de negocio ni acceso a datos aquí.
"""
from app.controllers.torneo_controller import TorneoController
from app.views.menu_torneo import MenuTorneo
from app.views.menu_resultados import MenuResultados


class MenuPrincipal:
    """Punto de entrada de la interfaz de consola del sistema."""

    OPCIONES = {
        '1': 'Gestionar Torneos',
        '2': 'Ver Resultados y Tabla',
        '0': 'Salir',
    }

    def __init__(
        self,
        torneo_controller: TorneoController,
        menu_torneo: MenuTorneo,
        menu_resultados: MenuResultados,
    ) -> None:
        self._torneo_controller = torneo_controller
        self._menu_torneo = menu_torneo
        self._menu_resultados = menu_resultados

    def mostrar(self) -> None:
        """Bucle principal del menú."""
        print("\n" + "=" * 55)
        print("  🏆  PLATAFORMA DE REGISTRO DE TORNEOS  🏐🏟")
        print("     Fútbol y Voley  |  Grupo 6 · UTP 2025")
        print("=" * 55)

        while True:
            print("\n── MENÚ PRINCIPAL ──────────────────────────────")
            for clave, descripcion in self.OPCIONES.items():
                print(f"  [{clave}] {descripcion}")
            print("─" * 48)

            opcion = input("Seleccione una opción: ").strip()

            if opcion == '1':
                self._menu_torneo.mostrar()
            elif opcion == '2':
                self._menu_resultados.mostrar()
            elif opcion == '0':
                print("\n¡Hasta pronto! 👋\n")
                break
            else:
                print("⚠  Opción no válida. Intente de nuevo.")
