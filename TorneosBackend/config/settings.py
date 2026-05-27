"""
Configuración global del sistema: variables de entorno y constantes.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.environ.get('DATABASE_URL', '')

# ── Constantes de dominio ───────────────────────────────────────────────────
MAX_EQUIPOS_FUTBOL: int = 10
MAX_EQUIPOS_VOLEY: int = 10
MIN_EQUIPOS: int = 2

PUNTOS_VICTORIA_FUTBOL: int = 3
PUNTOS_EMPATE_FUTBOL: int = 1
PUNTOS_DERROTA_FUTBOL: int = 0

PUNTOS_VICTORIA_VOLEY: int = 3
PUNTOS_DERROTA_VOLEY: int = 0

DEPORTES_VALIDOS = frozenset({'futbol', 'voley'})

# ── Logging ─────────────────────────────────────────────────────────────────
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s │ %(name)s │ %(levelname)s │ %(message)s',
    handlers=[
        logging.FileHandler('logs/torneos_error.log'),
        logging.StreamHandler(),
    ],
)
