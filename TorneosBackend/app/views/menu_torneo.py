"""
Vista: Menú de Torneos, Inscripción de Equipos y Fixture.
Adaptado al nuevo schema: IDs enteros, nombre_torneo, numero_equipos, id_deporte.
"""
from app.controllers.torneo_controller import TorneoController
from app.controllers.inscripcion_controller import InscripcionController
from app.controllers.fixture_controller import FixtureController


class MenuTorneo:
    """Menú de consola para gestión de torneos, inscripciones y fixture."""

    OPCIONES = {
        '1': 'Crear torneo',
        '2': 'Listar torneos',
        '3': 'Ver deportes disponibles',
        '4': 'Inscribir equipo',
        '5': 'Ver equipos de un torneo',
        '6': 'Generar fixture',
        '7': 'Ver fixture',
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
                '3': self._ver_deportes,
                '4': self._inscribir_equipo,
                '5': self._ver_equipos,
                '6': self._generar_fixture,
                '7': self._ver_fixture,
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
    def _ver_deportes(self) -> None:
        print("\n── Deportes Disponibles ─────────────────────────")
        exito, mensaje, deportes = self._torneo.listar_deportes()
        print(f"{'✔' if exito else '✗'}  {mensaje}")
        for d in deportes:
            print(f"   [{d['id_deporte']}] {d['nombre_deporte']} — {d['reglas']}")

    def _crear_torneo(self) -> None:
        print("\n── Crear Torneo ─────────────────────────────────")
        # Mostrar deportes disponibles para elegir
        _, _, deportes = self._torneo.listar_deportes()
        if deportes:
            print("Deportes disponibles:")
            for d in deportes:
                print(f"  [{d['id_deporte']}] {d['nombre_deporte']}")

        tipo = input("Tipo de deporte (futbol/voley): ").strip()
        id_deporte = input("ID del deporte: ").strip()
        nombre = input("Nombre del torneo: ").strip()
        numero_equipos = input("Número de equipos: ").strip()
        fecha = input("Fecha de inicio (YYYY-MM-DD): ").strip()

        exito, mensaje, datos = self._torneo.crear(
            tipo_deporte=tipo,
            nombre_torneo=nombre,
            numero_equipos=numero_equipos,
            fecha_inicio_str=fecha,
            id_deporte=id_deporte,
        )
        self._mostrar_resultado(exito, mensaje)
        if datos:
            print(f"   ID del torneo: {datos['id_torneo']}")

    def _listar_torneos(self) -> None:
        print("\n── Lista de Torneos ─────────────────────────────")
        exito, mensaje, torneos = self._torneo.listar()
        print(f"{'✔' if exito else '✗'}  {mensaje}")
        for t in torneos:
            print(
                f"   [{t['id_torneo']}] {t['nombre_torneo']} "
                f"| {t['nombre_deporte'].upper()} "
                f"| Equipos: {t['numero_equipos']} "
                f"| Inicio: {t['fecha_inicio']}"
            )

    def _inscribir_equipo(self) -> None:
        print("\n── Inscribir Equipo ─────────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        nombre = input("Nombre del equipo: ").strip()
        numero_jugadores = input("Número de jugadores: ").strip()

        exito, mensaje, datos = self._inscripcion.inscribir(
            nombre_equipo=nombre,
            numero_jugadores=numero_jugadores,
            id_torneo=id_torneo,
        )
        self._mostrar_resultado(exito, mensaje)
        if datos:
            print(f"   ID del equipo: {datos['id_equipo']}")

    def _ver_equipos(self) -> None:
        print("\n── Equipos del Torneo ───────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        exito, mensaje, equipos = self._inscripcion.listar_equipos(id_torneo)
        print(f"{'✔' if exito else '✗'}  {mensaje}")
        for e in equipos:
            print(
                f"   [{e['id_equipo']}] {e['nombre_equipo']:30s} "
                f"| Jugadores: {e['numero_jugadores']}"
            )

    def _generar_fixture(self) -> None:
        print("\n── Generar Fixture ──────────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        id_cancha = input("ID de la cancha: ").strip()
        fecha = input("Fecha base (YYYY-MM-DD, opcional, Enter para omitir): ").strip()

        exito, mensaje, partidos = self._fixture.generar(
            id_torneo=id_torneo,
            id_cancha=id_cancha,
            fecha_inicio_str=fecha if fecha else None,
        )
        self._mostrar_resultado(exito, mensaje)

    def _ver_fixture(self) -> None:
        print("\n── Fixture del Torneo ───────────────────────────")
        id_torneo = input("ID del torneo: ").strip()
        exito, mensaje, partidos = self._fixture.ver_fixture(id_torneo)
        print(f"{'✔' if exito else '✗'}  {mensaje}")
        for p in partidos:
            estado = p.get('estado', '?')
            print(
                f"   [{p['id_partido']}] {p['equipo_local']:20s} vs "
                f"{p['equipo_visitante']:20s} | {p.get('fecha','?')} | {estado}"
            )

    @staticmethod
    def _mostrar_resultado(exito: bool, mensaje: str) -> None:
        icono = '✔' if exito else '✗'
        print(f"\n{icono}  {mensaje}")
