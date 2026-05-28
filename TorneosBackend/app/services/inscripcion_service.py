"""
Servicio de lógica de negocio para la inscripción de equipos.
"""
import html
import re

from app.exceptions import EquipoDuplicadoError
from app.models.equipo import Equipo
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.torneo_repo import TorneoRepository


class InscripcionService:
    """Valida y registra equipos en torneos."""

    def __init__(
        self,
        equipo_repo: EquipoRepository,
        torneo_repo: TorneoRepository,
    ) -> None:
        self._equipo_repo = equipo_repo
        self._torneo_repo = torneo_repo

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
