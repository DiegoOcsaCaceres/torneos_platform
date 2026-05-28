"""
Vista: Menú de Resultados y Tabla de Posiciones.
Delega toda la lógica al ResultadoController.
"""
from app.controllers.resultado_controller import ResultadoController


class MenuResultados:
    """Menú de consola para registro de resultados y consulta de tabla."""

    OPCIONES = {
        '1': 'Registrar resultado de partido',
        '2': 'Ver tabla de posiciones',
        '3': 'Consultar resultado de partido',
        '0': 'Volver al menú principal',
    }

    def __init__(self, resultado_ctrl: ResultadoController) -> None:
        self._ctrl = resultado_ctrl

    def mostrar(self) -> None:
        """Bucle del menú de resultados."""
        while True:
            print("\n── RESULTADOS Y TABLA ──────────────────────────")
            for clave, descripcion in self.OPCIONES.items():
                print(f"  [{clave}] {descripcion}")
            print("─" * 48)

            opcion = input("Seleccione una opción: ").strip()

            if opcion == '1':
                self._registrar_resultado()
            elif opcion == '2':
                self._ver_tabla()
            elif opcion == '3':
                self._ver_resultado()
            elif opcion == '0':
                break
            else:
                print("⚠  Opción no válida.")

    # ── Acciones ──────────────────────────────────────────────────────────
    def _registrar_resultado(self) -> None:
        print("\n── Registrar Resultado ──────────────────────────")
        id_partido = input("ID del partido: ").strip()
        id_local = input("ID del equipo local: ").strip()
        id_visita = input("ID del equipo visitante: ").strip()
        id_torneo = input("ID del torneo: ").strip()
        marcador_local = input("Marcador local: ").strip()
        marcador_visita = input("Marcador visitante: ").strip()

        exito, mensaje, _ = self._ctrl.registrar(
            id_partido_str=id_partido,
            id_equipo_local_str=id_local,
            id_equipo_visita_str=id_visita,
            id_torneo_str=id_torneo,
            marcador_local_str=marcador_local,
            marcador_visita_str=marcador_visita,
        )
        self._mostrar_resultado(exito, mensaje)

    def _ver_tabla(self) -> None:
        print("\n── Tabla de Posiciones ──────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        exito, mensaje, tabla = self._ctrl.ver_tabla(id_torneo)
        print(f"{'✔' if exito else '✗'}  {mensaje}\n")

        if tabla:
            encabezado = f"  {'Pos':3}  {'Equipo':28}  {'Pts':4}  {'PG':4}  {'PE':4}  {'PP':4}"
            print(encabezado)
            print("  " + "─" * (len(encabezado) - 2))
            for pos, fila in enumerate(tabla, start=1):
                nombre = fila.get('equipos', {}).get('nombre', fila.get('id_equipo', '?')[:8])
                print(
                    f"  {pos:<3}  {nombre:<28}  {fila['puntos']:<4}  "
                    f"{fila['pg']:<4}  {fila['pe']:<4}  {fila['pp']:<4}"
                )

    def _ver_resultado(self) -> None:
        print("\n── Resultado de Partido ─────────────────────────")
        id_partido = input("ID del partido: ").strip()
        exito, mensaje, resultado = self._ctrl.ver_resultado(id_partido)
        self._mostrar_resultado(exito, mensaje)
        if resultado:
            print(
                f"   Marcador: {resultado['marcador_local']} - {resultado['marcador_visita']}"
            )

    @staticmethod
    def _mostrar_resultado(exito: bool, mensaje: str) -> None:
        icono = '✔' if exito else '✗'
        print(f"\n{icono}  {mensaje}")
