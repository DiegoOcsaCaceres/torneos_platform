"""
Servicio de lógica de negocio para la inscripción de equipos.
"""
import html
import re
from typing import Optional

from app.exceptions import EquipoDuplicadoError, JugadorDuplicadoError, EquipoConJugadoresError
from app.models.equipo import Equipo
from app.models.jugador import Jugador
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.jugador_repo import JugadorRepository
from app.repositories.torneo_repo import TorneoRepository


class InscripcionService:
    """Valida y registra equipos en torneos."""

    def __init__(
        self,
        equipo_repo: EquipoRepository,
        torneo_repo: TorneoRepository,
        jugador_repo: JugadorRepository = None,
    ) -> None:
        self._equipo_repo = equipo_repo
        self._torneo_repo = torneo_repo
        self._jugador_repo = jugador_repo or JugadorRepository()

    @staticmethod
    def _sanitizar(valor: str, max_len: int = 100) -> str:
        if not isinstance(valor, str):
            raise TypeError("Se esperaba una cadena de texto.")
        valor = valor.strip()
        valor = html.escape(valor)
        valor = re.sub(r'[<>"\';]', '', valor)
        if not valor or len(valor) > max_len:
            raise ValueError(f"El texto debe tener entre 1 y {max_len} caracteres.")
        return valor

    def inscribir_equipo(
        self,
        nombre_equipo: str,
        numero_jugadores: int,
        id_torneo: int,
    ) -> dict:
        """
        Valida y registra un equipo en el torneo.

        Args:
            nombre_equipo:    Nombre del equipo.
            numero_jugadores: Cantidad de jugadores.
            id_torneo:        ID del torneo al que se inscribe.

        Returns:
            dict con los datos del equipo creado.

        Raises:
            ValueError:           Si los datos de entrada son inválidos.
            EquipoDuplicadoError: Si el equipo ya existe en el torneo.
            RepositorioError:     Si ocurre un error de base de datos.
        """
        # 1. Sanitizar nombre
        nombre_equipo = self._sanitizar(nombre_equipo)

        # 2. Validar numero_jugadores
        if not isinstance(numero_jugadores, int) or numero_jugadores < 1:
            raise ValueError("El número de jugadores debe ser un entero positivo.")

        # 3. Verificar que el torneo existe
        torneo = self._torneo_repo.obtener_por_id(id_torneo)
        if not torneo:
            raise ValueError(f"No existe el torneo con ID: {id_torneo}")

        # 4. Verificar cupo disponible
        total = self._equipo_repo.contar_en_torneo(id_torneo)
        if total >= torneo['numero_equipos']:
            raise ValueError(
                f"El torneo ya alcanzó el límite de {torneo['numero_equipos']} equipos."
            )

        # 5. Verificar duplicados
        if self._equipo_repo.existe_en_torneo(nombre_equipo, id_torneo):
            raise EquipoDuplicadoError(
                f"El equipo '{nombre_equipo}' ya está inscrito en este torneo."
            )

        # 6. Crear y persistir
        equipo = Equipo(
            nombre_equipo=nombre_equipo,
            numero_jugadores=numero_jugadores,
            id_torneo=id_torneo,
        )
        return self._equipo_repo.guardar(equipo)

    def listar_equipos(self, id_torneo: int) -> list:
        """Retorna todos los equipos de un torneo."""
        return self._equipo_repo.listar_por_torneo(id_torneo)

    @staticmethod
    def _validar_edad(edad: Optional[int]) -> Optional[int]:
        if edad is None:
            return None
        if not isinstance(edad, int) or edad < 5 or edad > 99:
            raise ValueError("La edad debe ser un entero entre 5 y 99 años.")
        return edad

    @staticmethod
    def _validar_foto(foto: Optional[str]) -> Optional[str]:
        if not foto:
            return None
        if not isinstance(foto, str):
            raise TypeError("La foto debe ser una cadena en formato Base64.")
        # ~1.5MB en Base64 (equivalente al límite validado en el frontend)
        if len(foto) > 2_100_000:
            raise ValueError("La imagen es muy grande. El límite es de 1.5MB.")
        return foto

    def inscribir_jugador(
        self,
        nombre_jugador: str,
        apellido_paterno: str,
        apellido_materno: str,
        dni: str,
        id_equipo: int,
        edad: Optional[int] = None,
        foto: Optional[str] = None,
    ) -> dict:
        """
        Valida y registra un jugador en el equipo indicado.

        Args:
            nombre_jugador:   Nombre del jugador.
            apellido_paterno: Apellido paterno.
            apellido_materno: Apellido materno.
            dni:              Documento de identidad (único en todo el sistema).
            id_equipo:        ID del equipo al que pertenece.
            edad:             Edad del jugador (opcional).
            foto:             Foto del jugador en Base64 (opcional).

        Returns:
            dict con los datos del jugador creado.

        Raises:
            ValueError:            Si los datos de entrada son inválidos.
            JugadorDuplicadoError: Si el DNI ya está registrado.
            RepositorioError:      Si ocurre un error de base de datos.
        """
        nombre_jugador = self._sanitizar(nombre_jugador, max_len=50)
        apellido_paterno = self._sanitizar(apellido_paterno, max_len=50)
        apellido_materno = self._sanitizar(apellido_materno, max_len=50)
        dni = self._sanitizar(dni, max_len=15)
        edad = self._validar_edad(edad)
        foto = self._validar_foto(foto)

        equipo = self._equipo_repo.obtener_por_id(id_equipo)
        if not equipo:
            raise ValueError(f"No existe el equipo con ID: {id_equipo}")

        if self._jugador_repo.existe_dni_en_torneo(dni, equipo['id_torneo']):
            raise JugadorDuplicadoError(
                f"Ya existe un jugador registrado con el DNI '{dni}' en este torneo."
            )

        jugador = Jugador(
            nombre_jugador=nombre_jugador,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            DNI=dni,
            id_equipo=id_equipo,
            edad=edad,
            foto=foto,
        )
        return self._jugador_repo.guardar(jugador)

    def listar_jugadores(self, id_equipo: int) -> list:
        """Retorna todos los jugadores de un equipo."""
        return self._jugador_repo.listar_por_equipo(id_equipo)

    def actualizar_equipo(self, id_equipo: int, nombre_equipo: str, id_torneo: int) -> dict:
        """
        Renombra un equipo, validando que el nuevo nombre no choque con otro
        equipo ya existente en el mismo torneo.
        """
        nombre_equipo = self._sanitizar(nombre_equipo)

        equipo_actual = self._equipo_repo.obtener_por_id(id_equipo)
        if not equipo_actual:
            raise ValueError(f"No existe el equipo con ID: {id_equipo}")

        if self._equipo_repo.existe_en_torneo(nombre_equipo, id_torneo) and \
           nombre_equipo.lower() != equipo_actual['nombre_equipo'].lower():
            raise EquipoDuplicadoError(
                f"El equipo '{nombre_equipo}' ya está inscrito en este torneo."
            )

        return self._equipo_repo.actualizar_nombre(id_equipo, nombre_equipo)

    def eliminar_equipo(self, id_equipo: int) -> None:
        """
        Elimina un equipo, siempre que no tenga jugadores inscritos.
        """
        equipo = self._equipo_repo.obtener_por_id(id_equipo)
        if not equipo:
            raise ValueError(f"No existe el equipo con ID: {id_equipo}")

        total_jugadores = self._jugador_repo.contar_por_equipo(id_equipo)
        if total_jugadores > 0:
            raise EquipoConJugadoresError(
                f"No se puede eliminar el equipo '{equipo['nombre_equipo']}' "
                f"porque tiene {total_jugadores} jugador(es) inscrito(s). "
                "Elimina primero a los jugadores."
            )

        self._equipo_repo.eliminar(id_equipo)

    def actualizar_jugador(
        self,
        id_jugador: int,
        nombre_jugador: str,
        apellido_paterno: str,
        apellido_materno: str,
        dni: str,
        edad: Optional[int] = None,
        foto: Optional[str] = None,
    ) -> dict:
        """
        Actualiza los datos de un jugador, validando el DNI si cambió.
        Si 'edad' o 'foto' no se envían, se conserva el valor que ya
        tenía el jugador en la base de datos (no se pisan con NULL).
        """
        nombre_jugador = self._sanitizar(nombre_jugador, max_len=50)
        apellido_paterno = self._sanitizar(apellido_paterno, max_len=50)
        apellido_materno = self._sanitizar(apellido_materno, max_len=50)
        dni = self._sanitizar(dni, max_len=15)
        edad = self._validar_edad(edad)
        foto = self._validar_foto(foto)

        jugador_actual = self._jugador_repo.obtener_por_id(id_jugador)
        if not jugador_actual:
            raise ValueError(f"No existe el jugador con ID: {id_jugador}")

        if dni != jugador_actual['dni']:
            equipo = self._equipo_repo.obtener_por_id(jugador_actual['id_equipo'])
            if not equipo:
                raise ValueError(f"No existe el equipo con ID: {jugador_actual['id_equipo']}")
            if self._jugador_repo.existe_dni_en_torneo(dni, equipo['id_torneo'], excluir_id_jugador=id_jugador):
                raise JugadorDuplicadoError(
                    f"Ya existe un jugador registrado con el DNI '{dni}' en este torneo."
                )

        edad_final = edad if edad is not None else jugador_actual.get('edad')
        foto_final = foto if foto is not None else jugador_actual.get('foto')

        return self._jugador_repo.actualizar(
            id_jugador=id_jugador,
            nombre_jugador=nombre_jugador,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            dni=dni,
            edad=edad_final,
            foto=foto_final,
        )

    def eliminar_jugador(self, id_jugador: int) -> None:
        """Elimina un jugador por su ID."""
        jugador = self._jugador_repo.obtener_por_id(id_jugador)
        if not jugador:
            raise ValueError(f"No existe el jugador con ID: {id_jugador}")
        self._jugador_repo.eliminar(id_jugador)