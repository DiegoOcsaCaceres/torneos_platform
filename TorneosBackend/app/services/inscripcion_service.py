"""
Servicio de lógica de negocio para la inscripción de equipos (RF-03, RF-04).
"""
import html
import re
from uuid import UUID

from app.exceptions import EquipoDuplicadoError
from app.models.equipo import Equipo
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.torneo_repo import TorneoRepository
from config.settings import DEPORTES_VALIDOS


class InscripcionService:
    """
    Valida y registra equipos en torneos.
    Implementa RF-03 (registro de equipos) y RF-04 (unicidad de nombre).
    """

    def __init__(
        self,
        equipo_repo: EquipoRepository,
        torneo_repo: TorneoRepository,
    ) -> None:
        self._equipo_repo = equipo_repo
        self._torneo_repo = torneo_repo

    # ── Utilidades de sanitización ────────────────────────────────────────
    @staticmethod
    def _sanitizar(valor: str, max_len: int = 80) -> str:
        """Sanitiza una cadena de texto de entrada del usuario."""
        if not isinstance(valor, str):
            raise TypeError("Se esperaba una cadena de texto.")
        valor = valor.strip()
        valor = html.escape(valor)
        valor = re.sub(r'[<>"\';]', '', valor)
        if not valor or len(valor) > max_len:
            raise ValueError(
                f"El texto debe tener entre 1 y {max_len} caracteres."
            )
        return valor

    # ── Lógica principal ──────────────────────────────────────────────────
    def inscribir_equipo(
        self,
        nombre: str,
        deporte: str,
        id_torneo: UUID,
    ) -> dict:
        """
        Valida y registra un equipo en el torneo.

        Args:
            nombre:    Nombre del equipo (1-80 caracteres).
            deporte:   Disciplina deportiva ('futbol' o 'voley').
            id_torneo: UUID del torneo al que se inscribe.

        Returns:
            dict con los datos del equipo creado.

        Raises:
            ValueError:           Si los datos de entrada son inválidos.
            EquipoDuplicadoError: Si el equipo ya existe en el torneo.
            RepositorioError:     Si ocurre un error de base de datos.
        """
        # 1. Validar y sanitizar nombre
        nombre = self._sanitizar(nombre, max_len=80)

        # 2. Validar deporte
        deporte = deporte.strip().lower()
        if deporte not in DEPORTES_VALIDOS:
            raise ValueError(
                f"Deporte inválido: '{deporte}'. Opciones: {sorted(DEPORTES_VALIDOS)}"
            )

        # 3. Verificar que el torneo existe y está activo
        torneo = self._torneo_repo.obtener_por_id(id_torneo)
        if not torneo:
            raise ValueError(f"No existe el torneo con ID: {id_torneo}")
        if torneo['estado'] == 'finalizado':
            raise ValueError("No se pueden inscribir equipos en un torneo finalizado.")

        # 4. Verificar cupo disponible
        total = self._equipo_repo.contar_en_torneo(id_torneo)
        if total >= torneo['max_equipos']:
            raise ValueError(
                f"El torneo ya alcanzó el límite de {torneo['max_equipos']} equipos."
            )

        # 5. Verificar duplicados (RF-04)
        if self._equipo_repo.existe_en_torneo(nombre, id_torneo):
            raise EquipoDuplicadoError(
                f"El equipo '{nombre}' ya está inscrito en este torneo."
            )

        # 6. Crear instancia de dominio y persistir
        equipo = Equipo(nombre=nombre, deporte=deporte, id_torneo=id_torneo)
        return self._equipo_repo.guardar(equipo)

    def listar_equipos(self, id_torneo: UUID) -> list:
        """Retorna todos los equipos activos de un torneo."""
        return self._equipo_repo.listar_por_torneo(id_torneo)
