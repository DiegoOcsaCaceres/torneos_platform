"""
Vista: Menú de Resultados y Tabla de Posiciones.
Adaptado al nuevo schema: IDs enteros, puntaje por Partido_Equipo.
"""
from app.controllers.resultado_controller import ResultadoController


class MenuResultados:
    """Menú de consola para registro de resultados y consulta de tabla."""

    OPCIONES = {
        '1': 'Registrar resultado de partido',
        '2': 'Ver tabla de posiciones',
        '3': 'Ver marcador de un partido',
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
                self._ver_marcador()
            elif opcion == '0':
                break
            else:
                print("⚠  Opción no válida.")

    # ── Acciones ──────────────────────────────────────────────────────────
    def _registrar_resultado(self) -> None:
        print("\n── Registrar Resultado ──────────────────────────")
        print("  (Obtenga los IDs de Partido_Equipo desde 'Ver fixture')")
        id_partido = input("ID del partido: ").strip()
        id_pe_local = input("ID Partido_Equipo del local: ").strip()
        id_pe_visita = input("ID Partido_Equipo del visitante: ").strip()
        id_torneo = input("ID del torneo: ").strip()
        puntaje_local = input("Puntaje del local: ").strip()
        puntaje_visita = input("Puntaje del visitante: ").strip()

        exito, mensaje, _ = self._ctrl.registrar(
            id_partido_str=id_partido,
            id_pe_local_str=id_pe_local,
            id_pe_visita_str=id_pe_visita,
            id_torneo_str=id_torneo,
            puntaje_local_str=puntaje_local,
            puntaje_visita_str=puntaje_visita,
        )
        self._mostrar_msg(exito, mensaje)

    def _ver_tabla(self) -> None:
        print("\n── Tabla de Posiciones ──────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        exito, mensaje, tabla = self._ctrl.ver_tabla(id_torneo)
        print(f"{'✔' if exito else '✗'}  {mensaje}\n")

        if tabla:
            print(f"  {'Pos':3}  {'Equipo':30}  {'Pts':4}  {'PJ':4}  {'PG':4}")
            print("  " + "─" * 52)
            for pos, fila in enumerate(tabla, start=1):
                print(
                    f"  {pos:<3}  {fila['nombre_equipo']:<30}  "
                    f"{fila['puntos_totales']:<4}  "
                    f"{fila['partidos_jugados']:<4}  "
                    f"{fila['partidos_ganados']:<4}"
                )

    def _ver_marcador(self) -> None:
        print("\n── Marcador de Partido ──────────────────────────")
        id_partido = input("ID del partido: ").strip()
        exito, mensaje, marcador = self._ctrl.ver_marcador(id_partido)
        self._mostrar_msg(exito, mensaje)
        for fila in marcador:
            print(
                f"   {fila['nombre_condicion']:10} | "
                f"{fila['nombre_equipo']:25} | "
                f"Puntaje: {fila['puntaje']}"
            )

    @staticmethod
    def _mostrar_msg(exito: bool, mensaje: str) -> None:
        print(f"\n{'✔' if exito else '✗'}  {mensaje}")
