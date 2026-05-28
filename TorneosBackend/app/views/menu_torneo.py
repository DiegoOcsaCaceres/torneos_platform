"""
Vista: Menú de Torneos e Inscripción de Equipos.
Delega toda la lógica a los controllers correspondientes.
"""
from app.controllers.torneo_controller import TorneoController
from app.controllers.inscripcion_controller import InscripcionController
from app.controllers.fixture_controller import FixtureController


class MenuTorneo:
    """Menú de consola para gestión de torneos, inscripciones y fixture."""

    OPCIONES = {
        '1': 'Crear torneo',
        '2': 'Listar torneos',
        '3': 'Inscribir equipo',
        '4': 'Ver equipos de un torneo',
        '5': 'Generar fixture',
        '6': 'Ver fixture',
        '7': 'Iniciar torneo',
        '8': 'Finalizar torneo',
        '0': 'Volver al menú principal',
    }

    def __init__(
        self,
        torneo_ctrl: TorneoController,
        inscripcion_ctrl: InscripcionController,
        fixture_ctrl: FixtureController,
    ) -> None:
        self._torneo = torneo_ctrl
        self._inscripcion = inscripcion_ctrl
        self._fixture = fixture_ctrl

    def mostrar(self) -> None:
        """Bucle del menú de torneos."""
        while True:
            print("\n── GESTIÓN DE TORNEOS ──────────────────────────")
            for clave, descripcion in self.OPCIONES.items():
                print(f"  [{clave}] {descripcion}")
            print("─" * 48)

            opcion = input("Seleccione una opción: ").strip()

            acciones = {
                '1': self._crear_torneo,
                '2': self._listar_torneos,
                '3': self._inscribir_equipo,
                '4': self._ver_equipos,
                '5': self._generar_fixture,
                '6': self._ver_fixture,
                '7': self._iniciar_torneo,
                '8': self._finalizar_torneo,
                '0': None,
            }

            if opcion == '0':
                break
            accion = acciones.get(opcion)
            if accion:
                accion()
            else:
                print("⚠  Opción no válida.")

    # ── Acciones ──────────────────────────────────────────────────────────
    def _crear_torneo(self) -> None:
        print("\n── Crear Torneo ─────────────────────────────────")
        tipo = input("Tipo de deporte (futbol/voley): ").strip()
        nombre = input("Nombre del torneo: ").strip()
        max_equipos = input("Máximo de equipos (2-20): ").strip()
        fecha = input("Fecha de inicio (YYYY-MM-DD): ").strip()

        exito, mensaje, datos = self._torneo.crear(tipo, nombre, max_equipos, fecha)
        self._mostrar_resultado(exito, mensaje)
        if datos:
            print(f"   ID del torneo: {datos['id']}")

    def _listar_torneos(self) -> None:
        print("\n── Lista de Torneos ─────────────────────────────")
        exito, mensaje, torneos = self._torneo.listar()
        print(f"{'✔' if exito else '✗'}  {mensaje}")
        for t in torneos:
            print(
                f"   [{t['id']}] {t['nombre']} | {t['tipo_deporte'].upper()} "
                f"| {t['estado']} | Max: {t['max_equipos']} equipos"
            )

    def _inscribir_equipo(self) -> None:
        print("\n── Inscribir Equipo ─────────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        nombre = input("Nombre del equipo: ").strip()
        deporte = input("Deporte (futbol/voley): ").strip()

        exito, mensaje, datos = self._inscripcion.inscribir(nombre, deporte, id_torneo)
        self._mostrar_resultado(exito, mensaje)

    def _ver_equipos(self) -> None:
        print("\n── Equipos del Torneo ───────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        exito, mensaje, equipos = self._inscripcion.listar_equipos(id_torneo)
        print(f"{'✔' if exito else '✗'}  {mensaje}")
        for e in equipos:
            print(
                f"   {e['nombre']:30s} | Pts: {e['puntos']:3d} | "
                f"PJ:{e['partidos_jugados']} PG:{e['partidos_ganados']} "
                f"PE:{e['partidos_empatados']} PP:{e['partidos_perdidos']}"
            )

    def _generar_fixture(self) -> None:
        print("\n── Generar Fixture ──────────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        exito, mensaje, datos = self._fixture.generar(id_torneo)
        self._mostrar_resultado(exito, mensaje)

    def _ver_fixture(self) -> None:
        print("\n── Fixture del Torneo ───────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        exito, mensaje, partidos = self._fixture.ver_fixture(id_torneo)
        print(f"{'✔' if exito else '✗'}  {mensaje}")
        jornada_actual = None
        for p in partidos:
            if p['jornada'] != jornada_actual:
                jornada_actual = p['jornada']
                print(f"\n  ─── Jornada {jornada_actual} ───")
            estado = '✔ Jugado' if p['jugado'] else '⏳ Pendiente'
            print(
                f"   [{p['id'][:8]}...] "
                f"{p['id_equipo_local'][:8]}... vs {p['id_equipo_visita'][:8]}... "
                f"| {estado}"
            )

    def _iniciar_torneo(self) -> None:
        id_torneo = input("ID del torneo a iniciar: ").strip()
        exito, mensaje, _ = self._torneo.iniciar(id_torneo)
        self._mostrar_resultado(exito, mensaje)

    def _finalizar_torneo(self) -> None:
        id_torneo = input("ID del torneo a finalizar: ").strip()
        exito, mensaje, _ = self._torneo.finalizar(id_torneo)
        self._mostrar_resultado(exito, mensaje)

    # ── Utilidad ──────────────────────────────────────────────────────────
    @staticmethod
    def _mostrar_resultado(exito: bool, mensaje: str) -> None:
        icono = '✔' if exito else '✗'
        print(f"\n{icono}  {mensaje}")
